"""/start onboarding: university email (optional) and dorm building. Also /building."""

from __future__ import annotations

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from .. import keyboards, texts
from ..profile import WELCOME_IMAGE
from .common import cfg, db, is_onboarded, require_user, send_menu

EMAIL, BUILDING = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tg = update.effective_user
    user = db(context).upsert_user(tg.id, tg.username, tg.first_name)
    config = cfg(context)
    if is_onboarded(user, config):
        await send_menu(update, texts.READY.format(name=tg.first_name))
        return ConversationHandler.END
    await _send_welcome(update, context)
    if config.require_email and not user.email:
        await update.message.reply_html(texts.ASK_EMAIL.format(domains=texts.domains_text(config.university_email_domains)))
        return EMAIL
    await update.message.reply_html(texts.ASK_BUILDING, reply_markup=keyboards.buildings(config.buildings))
    return BUILDING


async def _send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome card with the cover image. Upload once, then reuse Telegram's file_id."""
    cached = context.bot_data.get("welcome_file_id")
    if cached:
        await update.message.reply_photo(cached, caption=texts.WELCOME, parse_mode="HTML")
        return
    with WELCOME_IMAGE.open("rb") as f:
        msg = await update.message.reply_photo(f, caption=texts.WELCOME, parse_mode="HTML")
    if msg.photo:
        context.bot_data["welcome_file_id"] = msg.photo[-1].file_id


async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    config = cfg(context)
    value = update.message.text.strip()
    if not texts.valid_university_email(value, config.university_email_domains):
        await update.message.reply_html(texts.BAD_EMAIL.format(domains=texts.domains_text(config.university_email_domains)))
        return EMAIL
    db(context).set_email(update.effective_user.id, value.lower())
    await update.message.reply_html(texts.ASK_BUILDING, reply_markup=keyboards.buildings(config.buildings))
    return BUILDING


async def building(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    idx = int(q.data.split(":")[1])
    name = cfg(context).buildings[idx]
    db(context).set_building(q.from_user.id, name)
    await q.answer()
    await q.edit_message_text(f"🏠 {name}")
    await send_menu(update, texts.READY.format(name=q.from_user.first_name))
    return ConversationHandler.END


async def change_building(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await require_user(update, context) is None:
        return
    await update.message.reply_html(texts.ASK_BUILDING, reply_markup=keyboards.buildings(cfg(context).buildings, "setbld"))


async def set_building(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    name = cfg(context).buildings[int(q.data.split(":")[1])]
    db(context).set_building(q.from_user.id, name)
    await q.answer("Saved")
    await q.edit_message_text(f"🏠 Your building is now {name}.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Setup paused. Send /start to continue.")
    return ConversationHandler.END


def handlers(persistent: bool = False) -> list:
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            BUILDING: [CallbackQueryHandler(building, pattern=r"^bld:\d+$")],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
        allow_reentry=True,
        persistent=persistent,
        name="onboarding",
    )
    return [
        conv,
        CommandHandler("building", change_building),
        CallbackQueryHandler(set_building, pattern=r"^setbld:\d+$"),
    ]
