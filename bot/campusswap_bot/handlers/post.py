"""Post an item: photo → title → category → condition → free/swap/sell (→ price) → pickup spot → time slots → publish."""

from __future__ import annotations

import re

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from .. import keyboards, texts
from .common import cfg, db, require_user, send_menu

PHOTO, TITLE, CATEGORY, CONDITION, KIND, PRICE, SPOT, SLOTS, CONFIRM = range(9)

MENU_FILTER = filters.Regex("^(" + "|".join(re.escape(b) for b in texts.MENU_BUTTONS) + ")$")
TEXT = filters.TEXT & ~filters.COMMAND & ~MENU_FILTER


def _draft(context: ContextTypes.DEFAULT_TYPE) -> dict:
    return context.user_data.setdefault("draft", {})


async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = await require_user(update, context)
    if user is None:
        return ConversationHandler.END
    context.user_data["draft"] = {}
    await update.message.reply_html(texts.POST_ASK_PHOTO)
    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    _draft(context)["photo"] = update.message.photo[-1].file_id  # largest size
    await update.message.reply_html(texts.POST_ASK_TITLE)
    return TITLE


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    _draft(context)["photo"] = None
    await update.message.reply_html(texts.POST_ASK_TITLE)
    return TITLE


async def title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text.strip()
    if not texts.valid_title(value):
        await update.message.reply_html(texts.POST_BAD_TITLE)
        return TITLE
    _draft(context)["title"] = value
    await update.message.reply_html(texts.POST_ASK_CATEGORY, reply_markup=keyboards.categories(cfg(context).categories))
    return CATEGORY


async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    name = cfg(context).categories[int(q.data.split(":")[1])]
    _draft(context)["category"] = name
    await q.answer()
    await q.edit_message_text(f"🏷 {name}")
    await q.message.reply_html(texts.POST_ASK_CONDITION, reply_markup=keyboards.conditions())
    return CONDITION


async def condition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    value = texts.CONDITIONS[int(q.data.split(":")[1])]
    _draft(context)["condition"] = value
    await q.answer()
    await q.edit_message_text(f"✨ {value}")
    await q.message.reply_html(texts.POST_ASK_KIND, reply_markup=keyboards.kinds())
    return KIND


async def _ask_spot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = db(context).get_user(update.effective_user.id)
    suggestion = f"{user.building} lobby" if user and user.building else "Main entrance"
    _draft(context)["suggested_spot"] = suggestion
    await update.effective_message.reply_html(texts.POST_ASK_SPOT, reply_markup=keyboards.spot_suggestion(suggestion))
    return SPOT


async def kind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    value = q.data.split(":")[1]
    _draft(context)["kind"] = value
    await q.answer()
    await q.edit_message_text(texts.KINDS[value])
    if value == "sell":
        await q.message.reply_html(texts.POST_ASK_PRICE)
        return PRICE
    _draft(context)["price"] = None
    return await _ask_spot(update, context)


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = texts.parse_price(update.message.text)
    if value is None:
        await update.message.reply_html(texts.POST_BAD_PRICE)
        return PRICE
    _draft(context)["price"] = value
    return await _ask_spot(update, context)


async def _ask_slots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.effective_message.reply_html(texts.POST_ASK_SLOTS.format(max=cfg(context).max_slots))
    return SLOTS


async def spot_default(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    d = _draft(context)
    d["spot"] = d.get("suggested_spot", "Main entrance")
    await q.answer()
    await q.edit_message_text(f"📍 {d['spot']}")
    return await _ask_slots(update, context)


async def spot_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text.strip()[:60]
    _draft(context)["spot"] = value
    return await _ask_slots(update, context)


async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    max_slots = cfg(context).max_slots
    value = texts.parse_slots(update.message.text, max_slots)
    if value is None:
        await update.message.reply_html(texts.POST_BAD_SLOTS.format(max=max_slots))
        return SLOTS
    d = _draft(context)
    d["slots"] = value
    preview = texts.draft_preview(d)
    if d.get("photo"):
        await update.message.reply_photo(d["photo"], caption=preview, parse_mode="HTML", reply_markup=keyboards.publish())
    else:
        await update.message.reply_html(preview, reply_markup=keyboards.publish())
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    await q.edit_message_reply_markup(None)
    d = context.user_data.pop("draft", {})
    if q.data == "pub:no":
        await send_menu(update, texts.CANCELLED)
        return ConversationHandler.END
    db(context).create_item(
        owner_id=q.from_user.id,
        title=d["title"],
        category=d["category"],
        condition=d["condition"],
        kind=d["kind"],
        price=d.get("price"),
        pickup_spot=d["spot"],
        slots=d["slots"],
        photo_file_id=d.get("photo"),
    )
    await send_menu(update, texts.POST_PUBLISHED)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("draft", None)
    await send_menu(update, texts.CANCELLED)
    return ConversationHandler.END


def handlers(persistent: bool = False) -> list:
    return [
        ConversationHandler(
            entry_points=[CommandHandler("post", begin), MessageHandler(filters.Regex(f"^{re.escape(texts.BTN_POST)}$"), begin)],
            states={
                PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
                TITLE: [MessageHandler(TEXT, title)],
                CATEGORY: [CallbackQueryHandler(category, pattern=r"^cat:\d+$")],
                CONDITION: [CallbackQueryHandler(condition, pattern=r"^cond:\d+$")],
                KIND: [CallbackQueryHandler(kind, pattern=r"^kind:(free|swap|sell)$")],
                PRICE: [MessageHandler(TEXT, price)],
                SPOT: [CallbackQueryHandler(spot_default, pattern=r"^spot:default$"), MessageHandler(TEXT, spot_text)],
                SLOTS: [MessageHandler(TEXT, slots)],
                CONFIRM: [CallbackQueryHandler(confirm, pattern=r"^pub:(yes|no)$")],
            },
            fallbacks=[CommandHandler("cancel", cancel), MessageHandler(MENU_FILTER, cancel)],
            allow_reentry=True,
            persistent=persistent,
            name="post_item",
        )
    ]
