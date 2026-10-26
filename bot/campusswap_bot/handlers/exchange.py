"""The exchange: request an item → owner accepts/declines → handover → rating."""

from __future__ import annotations

import logging
from html import escape

from telegram import Update
from telegram.error import Forbidden
from telegram.ext import CallbackQueryHandler, ContextTypes

from .. import keyboards, texts
from ..db import Request
from .common import db, require_user

log = logging.getLogger(__name__)


async def _notify(context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str, markup=None) -> bool:
    """Message another user. Returns False if they blocked the bot or never started it."""
    try:
        await context.bot.send_message(user_id, text, parse_mode="HTML", reply_markup=markup)
        return True
    except Forbidden:
        log.info("Cannot message user %s (blocked or never started the bot)", user_id)
        return False


async def choose_slot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    user = await require_user(update, context)
    if user is None:
        return
    item = db(context).get_item(int(q.data.split(":")[1]))
    if item is None or item.status != "active":
        await q.answer("Sorry, this item is no longer available.", show_alert=True)
        return
    if item.owner_id == user.id:
        await q.answer("This is your own item.", show_alert=True)
        return
    if db(context).open_request(item.id, user.id):
        await q.answer("You already requested this item. See 📥 My requests.", show_alert=True)
        return
    await q.answer()
    await q.message.reply_html(
        f"When do you want to pick up <b>{escape(item.title)}</b> at 📍 {escape(item.pickup_spot)}?",
        reply_markup=keyboards.slots(item.id, item.slots),
    )


async def cancel_slot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    await q.message.delete()


async def send_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    user = await require_user(update, context)
    if user is None:
        return
    _, item_id, idx = q.data.split(":")
    d = db(context)
    item = d.get_item(int(item_id))
    if item is None or item.status != "active" or item.owner_id == user.id:
        await q.answer("Sorry, this item is no longer available.", show_alert=True)
        return
    if d.open_request(item.id, user.id):
        await q.answer("You already requested this item.", show_alert=True)
        return
    slot = item.slots[int(idx)]
    req = d.create_request(item.id, user.id, slot)
    stats = d.stats(user.id)
    sent = await _notify(
        context,
        item.owner_id,
        f"🙋 {texts.mention(user)} from {escape(user.building or 'campus')} ({texts.rating_label(stats)}) "
        f"wants your <b>{escape(item.title)}</b>.\n🕒 Pickup: <b>{escape(slot)}</b> at 📍 {escape(item.pickup_spot)}",
        keyboards.owner_decision(req.id),
    )
    await q.answer()
    if not sent:
        d.set_request_status(req.id, "cancelled")
        await q.edit_message_text("Sorry, the owner can't be reached right now. Try another item.")
        return
    await q.edit_message_text(
        f"✅ Request sent for <b>{escape(item.title)}</b> ({escape(slot)}). You'll get a message when the owner answers.",
        parse_mode="HTML",
    )


async def _load_for_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple[Request, object] | None:
    q = update.callback_query
    req = db(context).get_request(int(q.data.split(":")[1]))
    item = db(context).get_item(req.item_id) if req else None
    if req is None or item is None or item.owner_id != q.from_user.id:
        await q.answer("This request is not yours.", show_alert=True)
        return None
    if req.status != "pending":
        await q.answer(f"This request is already {texts.STATUS_LABELS.get(req.status, req.status)}.", show_alert=True)
        return None
    return req, item


async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    loaded = await _load_for_owner(update, context)
    if loaded is None:
        return
    req, item = loaded
    d = db(context)
    if item.status != "active":
        await q.answer("You already agreed a pickup for this item.", show_alert=True)
        return
    d.set_request_status(req.id, "accepted")
    d.set_item_status(item.id, "reserved")
    owner, requester = d.get_user(item.owner_id), d.get_user(req.requester_id)
    for other in d.pending_requests_for_item(item.id):
        d.set_request_status(other.id, "declined")
        await _notify(context, other.requester_id, f"😔 <b>{escape(item.title)}</b> went to someone else. Keep browsing!")
    await q.answer("Accepted")
    await q.edit_message_text(
        f"🤝 You accepted. Meet {texts.mention(requester)} at 📍 {escape(item.pickup_spot)}, 🕒 <b>{escape(req.slot)}</b>.\n"
        "Tap <b>Handed over</b> after the exchange.",
        parse_mode="HTML",
        reply_markup=keyboards.handover(req.id),
    )
    await _notify(
        context,
        requester.id,
        f"🎉 {texts.mention(owner)} accepted your request for <b>{escape(item.title)}</b>!\n"
        f"📍 {escape(item.pickup_spot)} · 🕒 <b>{escape(req.slot)}</b>\n"
        "Tap the name to message them. Tap <b>Handed over</b> after the exchange.",
        keyboards.handover(req.id),
    )


async def decline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    loaded = await _load_for_owner(update, context)
    if loaded is None:
        return
    req, item = loaded
    db(context).set_request_status(req.id, "declined")
    await q.answer("Declined")
    await q.edit_message_text(f"❌ You declined this request for {escape(item.title)}.", parse_mode="HTML")
    await _notify(context, req.requester_id, f"😔 The owner can't give you <b>{escape(item.title)}</b> this time.")


async def _load_participant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    req = db(context).get_request(int(q.data.split(":")[1]))
    item = db(context).get_item(req.item_id) if req else None
    if req is None or item is None or q.from_user.id not in (item.owner_id, req.requester_id):
        await q.answer("This exchange is not yours.", show_alert=True)
        return None
    if req.status != "accepted":
        await q.answer(f"This exchange is already {texts.STATUS_LABELS.get(req.status, req.status)}.", show_alert=True)
        return None
    other_id = req.requester_id if q.from_user.id == item.owner_id else item.owner_id
    return req, item, other_id


async def handed_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    loaded = await _load_participant(update, context)
    if loaded is None:
        return
    req, item, other_id = loaded
    d = db(context)
    d.set_request_status(req.id, "completed")
    d.set_item_status(item.id, "given")
    me, other = d.get_user(q.from_user.id), d.get_user(other_id)
    await q.answer("Done!")
    await q.edit_message_text(f"✅ <b>{escape(item.title)}</b> handed over. 🌱 One more item saved from the trash!", parse_mode="HTML")
    await q.message.reply_html(f"How was the exchange with {escape(other.first_name)}?", reply_markup=keyboards.rating(req.id))
    await _notify(
        context,
        other.id,
        f"✅ {escape(me.first_name)} marked <b>{escape(item.title)}</b> as handed over.\n"
        f"How was the exchange with {escape(me.first_name)}?",
        keyboards.rating(req.id),
    )


async def cancel_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    loaded = await _load_participant(update, context)
    if loaded is None:
        return
    req, item, other_id = loaded
    d = db(context)
    d.set_request_status(req.id, "cancelled")
    d.set_item_status(item.id, "active")
    await q.answer("Cancelled")
    await q.edit_message_text(f"✖ Pickup of <b>{escape(item.title)}</b> cancelled. The item is available again.", parse_mode="HTML")
    await _notify(context, other_id, f"✖ The pickup of <b>{escape(item.title)}</b> was cancelled.")


async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    _, rid, stars = q.data.split(":")
    d = db(context)
    req = d.get_request(int(rid))
    item = d.get_item(req.item_id) if req else None
    if req is None or item is None or q.from_user.id not in (item.owner_id, req.requester_id) or req.status != "completed":
        await q.answer("You can't rate this exchange.", show_alert=True)
        return
    ratee = req.requester_id if q.from_user.id == item.owner_id else item.owner_id
    if not d.add_rating(req.id, q.from_user.id, ratee, int(stars)):
        await q.answer("You already rated this exchange.", show_alert=True)
        return
    await q.answer("Thanks!")
    await q.edit_message_text(f"Thanks for rating! {'⭐' * int(stars)}")


def handlers() -> list:
    return [
        CallbackQueryHandler(choose_slot, pattern=r"^req:\d+$"),
        CallbackQueryHandler(cancel_slot, pattern=r"^slotx$"),
        CallbackQueryHandler(send_request, pattern=r"^slot:\d+:\d+$"),
        CallbackQueryHandler(accept, pattern=r"^acc:\d+$"),
        CallbackQueryHandler(decline, pattern=r"^dec:\d+$"),
        CallbackQueryHandler(handed_over, pattern=r"^done:\d+$"),
        CallbackQueryHandler(cancel_pickup, pattern=r"^cxl:\d+$"),
        CallbackQueryHandler(rate, pattern=r"^rate:\d+:[1-5]$"),
    ]
