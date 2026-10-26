"""Message texts and small pure helpers (easy to unit test)."""

from __future__ import annotations

import re
from html import escape

from .db import Item, Stats, User

# Main menu buttons (reply keyboard). Handlers match on these exact strings.
BTN_BROWSE = "🔎 Browse"
BTN_POST = "➕ Post an item"
BTN_MY_ITEMS = "📦 My items"
BTN_MY_REQUESTS = "📥 My requests"
BTN_PROFILE = "👤 Profile"
BTN_HELP = "❓ Help"
MENU_BUTTONS = [BTN_BROWSE, BTN_POST, BTN_MY_ITEMS, BTN_MY_REQUESTS, BTN_PROFILE, BTN_HELP]

CONDITIONS = ["New", "Good", "Used"]
KINDS = {"free": "🆓 Free", "swap": "🔄 Swap", "sell": "💰 Sell"}

STATUS_LABELS = {
    "active": "🟢 available",
    "reserved": "🟡 reserved",
    "given": "✅ given away",
    "removed": "⚪ removed",
    "pending": "⏳ waiting for the owner",
    "accepted": "🤝 pickup agreed",
    "declined": "❌ declined",
    "cancelled": "⚪ cancelled",
    "completed": "✅ completed",
}

WELCOME = (
    "👋 <b>Welcome to CampusSwap!</b>\n\n"
    "Pass dorm items on to other students: give away, swap or sell, and agree on pickup right here."
)
ASK_EMAIL = "To keep CampusSwap students-only, send your <b>university email</b> (it must end with {domains})."
BAD_EMAIL = "That doesn't look like a university email. It must end with {domains}. Try again:"
ASK_BUILDING = "Which dorm building do you live in? Items from your building are shown first."
READY = "✅ You're all set, {name}! Use the menu below."

HELP = (
    "<b>How CampusSwap works</b>\n\n"
    f"{BTN_BROWSE}: see items from other students, your building first.\n"
    f"{BTN_POST}: list something you no longer need (under a minute).\n"
    "🙋 <b>Request</b> an item and pick one of the owner's pickup times.\n"
    "🤝 The owner accepts, you meet at the pickup spot, then tap <b>Handed over</b>.\n"
    "⭐ Rate each other to build trust.\n\n"
    "Commands: /browse /post /myitems /myrequests /profile /building /cancel"
)

POST_ASK_PHOTO = "📷 Send a photo of the item, or /skip if you don't have one."
POST_ASK_TITLE = "✏️ What is it? Send a short title, e.g. <i>Desk lamp, IKEA</i>."
POST_BAD_TITLE = "Please send a title between 3 and 60 characters."
POST_ASK_CATEGORY = "🏷 Choose a category:"
POST_ASK_CONDITION = "✨ What condition is it in?"
POST_ASK_KIND = "🤲 How do you want to pass it on?"
POST_ASK_PRICE = "💰 Price in rubles (numbers only, e.g. <i>150</i>):"
POST_BAD_PRICE = "Please send a whole number between 1 and 100000."
POST_ASK_SPOT = "📍 Where can people pick it up? Tap the suggestion or type a spot."
POST_ASK_SLOTS = (
    "🕒 When can people pick it up? Send up to {max} time slots separated by commas, e.g.\n"
    "<i>Today 18:00, Today 19:30, Tomorrow 12:00</i>"
)
POST_BAD_SLOTS = "Please send 1 to {max} time slots separated by commas (each up to 40 characters)."
POST_PUBLISHED = "🎉 Published! You'll get a message when someone requests it."
CANCELLED = "Cancelled. Use the menu below to continue."


def domains_text(domains: list[str]) -> str:
    return ", ".join(f"@{d}" for d in domains)


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})$")


def valid_university_email(email: str, domains: list[str]) -> bool:
    m = EMAIL_RE.match(email.strip())
    if not m:
        return False
    host = m.group(1).lower()
    return any(host == d or host.endswith("." + d) for d in domains)


def parse_slots(text: str, max_slots: int) -> list[str] | None:
    """Split 'Today 18:00, Tomorrow 12:00' into slots. Returns None if invalid."""
    slots = [s.strip() for s in text.split(",") if s.strip()]
    if not 1 <= len(slots) <= max_slots or any(len(s) > 40 for s in slots):
        return None
    return slots


def parse_price(text: str) -> int | None:
    t = text.strip().replace(" ", "").removesuffix("₽").removesuffix("rub")
    if not t.isdigit():
        return None
    value = int(t)
    return value if 1 <= value <= 100_000 else None


def valid_title(text: str) -> bool:
    return 3 <= len(text.strip()) <= 60


def price_label(item: Item) -> str:
    if item.kind == "free":
        return "🆓 FREE"
    if item.kind == "swap":
        return "🔄 SWAP"
    return f"💰 {item.price} ₽"


def rating_label(stats: Stats) -> str:
    if stats.rating is None:
        return "no ratings yet"
    return f"⭐ {stats.rating} ({stats.rating_count})"


def user_label(user: User) -> str:
    return escape(user.first_name) + (f" (@{escape(user.username)})" if user.username else "")


def mention(user: User) -> str:
    """A clickable HTML mention that works even without a @username."""
    return f'<a href="tg://user?id={user.id}">{escape(user.first_name)}</a>'


def item_caption(item: Item, owner: User, owner_stats: Stats, position: str | None = None) -> str:
    lines = [
        f"<b>{escape(item.title)}</b>   {price_label(item)}",
        f"🏷 {escape(item.category)} · ✨ {escape(item.condition)}",
        f"📍 {escape(item.pickup_spot)}",
        "🕒 " + " · ".join(escape(s) for s in item.slots),
        f"👤 {escape(owner.first_name)} · {escape(owner.building or 'campus')} · {rating_label(owner_stats)}",
    ]
    if position:
        lines.append(f"\n<i>{position}</i>")
    return "\n".join(lines)


def draft_preview(d: dict) -> str:
    price = {"free": "🆓 FREE", "swap": "🔄 SWAP"}.get(d["kind"], f"💰 {d.get('price')} ₽")
    return (
        "<b>Preview</b>\n\n"
        f"<b>{escape(d['title'])}</b>   {price}\n"
        f"🏷 {escape(d['category'])} · ✨ {escape(d['condition'])}\n"
        f"📍 {escape(d['spot'])}\n"
        "🕒 " + " · ".join(escape(s) for s in d["slots"]) + "\n\n"
        "Publish it?"
    )


def profile_text(user: User, stats: Stats) -> str:
    return (
        f"👤 <b>{escape(user.first_name)}</b>\n"
        f"🏠 {escape(user.building or 'not set')}\n"
        f"⭐ Rating: {rating_label(stats)}\n"
        f"📤 Items given: {stats.given}\n"
        f"📥 Items received: {stats.received}\n"
        f"🌱 Items saved from the trash: {stats.given + stats.received}\n\n"
        "Change your building with /building"
    )
