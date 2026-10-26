"""Browse items one card at a time, with category and free-only filters."""

from __future__ import annotations

import re

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from .. import keyboards, texts
from .common import cfg, db, require_user


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await require_user(update, context) is None:
        return
    await update.effective_message.reply_html(
        "What are you looking for?", reply_markup=keyboards.browse_categories(cfg(context).categories)
    )


async def menu_again(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    await _replace(q, context, text="What are you looking for?", markup=keyboards.browse_categories(cfg(context).categories))


async def _replace(q, context, text: str, markup, photo: str | None = None) -> None:
    """Replace the current card with a new message (cards can switch between photo and text)."""
    try:
        await q.message.delete()
    except BadRequest:
        pass
    if photo:
        await context.bot.send_photo(q.message.chat_id, photo, caption=text, parse_mode="HTML", reply_markup=markup)
    else:
        await context.bot.send_message(q.message.chat_id, text, parse_mode="HTML", reply_markup=markup)


async def navigate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    user = await require_user(update, context)
    if user is None:
        return
    _, cat, free, offset = q.data.split(":")
    free_i, offset_i = int(free), int(offset)
    category = None if cat == "a" else cfg(context).categories[int(cat)]
    items = db(context).browse_items(user.id, user.building, category, bool(free_i))
    await q.answer()
    if not items:
        scope = ("free " if free_i else "") + (f"items in {category}" if category else "items")
        await _replace(
            q, context,
            text=f"No {scope} right now. Try another category, or post something yourself with {texts.BTN_POST}.",
            markup=keyboards.browse_categories(cfg(context).categories),
        )
        return
    offset_i %= len(items)
    item = items[offset_i]
    owner = db(context).get_user(item.owner_id)
    caption = texts.item_caption(item, owner, db(context).stats(owner.id), position=f"{offset_i + 1} of {len(items)}")
    await _replace(q, context, text=caption, markup=keyboards.item_card(item.id, cat, free_i, offset_i, len(items)),
                   photo=item.photo_file_id)


def handlers() -> list:
    return [
        CommandHandler("browse", menu),
        MessageHandler(filters.Regex(f"^{re.escape(texts.BTN_BROWSE)}$"), menu),
        CallbackQueryHandler(menu_again, pattern=r"^brm$"),
        CallbackQueryHandler(navigate, pattern=r"^nav:(a|\d+):[01]:-?\d+$"),
    ]
