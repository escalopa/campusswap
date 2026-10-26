"""My items, my requests, profile and help."""

from __future__ import annotations

import re
from html import escape

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from .. import keyboards, texts
from .common import db, require_user, send_menu


def _button(text: str):
    return filters.Regex(f"^{re.escape(text)}$")


async def my_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await require_user(update, context)
    if user is None:
        return
    items = db(context).items_of(user.id)
    if not items:
        await send_menu(update, f"You haven't posted anything yet. Tap {texts.BTN_POST} to start.")
        return
    await update.effective_message.reply_html(f"📦 <b>Your items</b> ({len(items)})")
    for item in items[:15]:
        line = f"<b>{escape(item.title)}</b>   {texts.price_label(item)}\n{texts.STATUS_LABELS[item.status]}"
        markup = keyboards.remove_item(item.id) if item.status == "active" else None
        await update.effective_message.reply_html(line, reply_markup=markup)


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    d = db(context)
    item = d.get_item(int(q.data.split(":")[1]))
    if item is None or item.owner_id != q.from_user.id:
        await q.answer("This item is not yours.", show_alert=True)
        return
    if item.status != "active":
        await q.answer("Only available items can be removed.", show_alert=True)
        return
    d.set_item_status(item.id, "removed")
    await q.answer("Removed")
    await q.edit_message_text(f"🗑 <s>{escape(item.title)}</s> removed.", parse_mode="HTML")


async def my_requests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await require_user(update, context)
    if user is None:
        return
    d = db(context)
    reqs = d.requests_of(user.id)
    if not reqs:
        await send_menu(update, f"No requests yet. Tap {texts.BTN_BROWSE} to find something.")
        return
    lines = ["📥 <b>Your requests</b>\n"]
    for r in reqs:
        item = d.get_item(r.item_id)
        title = escape(item.title) if item else "deleted item"
        lines.append(f"• <b>{title}</b> · 🕒 {escape(r.slot)}\n   {texts.STATUS_LABELS.get(r.status, r.status)}")
    await send_menu(update, "\n".join(lines))


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await require_user(update, context)
    if user is None:
        return
    await send_menu(update, texts.profile_text(user, db(context).stats(user.id)))


async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_menu(update, texts.HELP)


def handlers() -> list:
    return [
        CommandHandler("myitems", my_items),
        MessageHandler(_button(texts.BTN_MY_ITEMS), my_items),
        CallbackQueryHandler(remove, pattern=r"^rm:\d+$"),
        CommandHandler("myrequests", my_requests),
        MessageHandler(_button(texts.BTN_MY_REQUESTS), my_requests),
        CommandHandler("profile", profile),
        MessageHandler(_button(texts.BTN_PROFILE), profile),
        CommandHandler("help", help_),
        MessageHandler(_button(texts.BTN_HELP), help_),
    ]
