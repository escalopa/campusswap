"""Inline and reply keyboards."""

from __future__ import annotations

from telegram import InlineKeyboardButton as B
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup

from . import texts


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[texts.BTN_BROWSE, texts.BTN_POST], [texts.BTN_MY_ITEMS, texts.BTN_MY_REQUESTS], [texts.BTN_PROFILE, texts.BTN_HELP]],
        resize_keyboard=True,
    )


def grid(buttons: list[B], cols: int = 2) -> list[list[B]]:
    return [buttons[i : i + cols] for i in range(0, len(buttons), cols)]


def buildings(names: list[str], prefix: str = "bld") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(grid([B(n, callback_data=f"{prefix}:{i}") for i, n in enumerate(names)]))


def categories(names: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(grid([B(n, callback_data=f"cat:{i}") for i, n in enumerate(names)]))


def conditions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[B(c, callback_data=f"cond:{i}") for i, c in enumerate(texts.CONDITIONS)]])


def kinds() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[B(label, callback_data=f"kind:{k}") for k, label in texts.KINDS.items()]])


def spot_suggestion(spot: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[B(f"📍 {spot}", callback_data="spot:default")]])


def publish() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[B("✅ Publish", callback_data="pub:yes"), B("✖ Cancel", callback_data="pub:no")]])


def browse_categories(names: list[str]) -> InlineKeyboardMarkup:
    rows = [[B("All items", callback_data="nav:a:0:0"), B("🆓 Free only", callback_data="nav:a:1:0")]]
    rows += grid([B(n, callback_data=f"nav:{i}:0:0") for i, n in enumerate(names)])
    return InlineKeyboardMarkup(rows)


def item_card(item_id: int, cat: str, free: int, offset: int, total: int) -> InlineKeyboardMarkup:
    rows = []
    if total > 1:
        rows.append([B("◀", callback_data=f"nav:{cat}:{free}:{offset - 1}"), B("▶", callback_data=f"nav:{cat}:{free}:{offset + 1}")])
    rows.append([B("🙋 Request", callback_data=f"req:{item_id}")])
    rows.append([
        B("🆓 Free only: " + ("on" if free else "off"), callback_data=f"nav:{cat}:{1 - free}:0"),
        B("🏷 Categories", callback_data="brm"),
    ])
    return InlineKeyboardMarkup(rows)


def slots(item_id: int, slot_list: list[str]) -> InlineKeyboardMarkup:
    rows = [[B(f"🕒 {s}", callback_data=f"slot:{item_id}:{i}")] for i, s in enumerate(slot_list)]
    rows.append([B("✖ Cancel", callback_data="slotx")])
    return InlineKeyboardMarkup(rows)


def owner_decision(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[B("✅ Accept", callback_data=f"acc:{request_id}"), B("❌ Decline", callback_data=f"dec:{request_id}")]])


def handover(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[B("✅ Handed over", callback_data=f"done:{request_id}"), B("✖ Cancel pickup", callback_data=f"cxl:{request_id}")]])


def rating(request_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[B("⭐" * n, callback_data=f"rate:{request_id}:{n}") for n in range(1, 6)][:3],
                                 [B("⭐" * n, callback_data=f"rate:{request_id}:{n}") for n in range(4, 6)]])


def remove_item(item_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[B("🗑 Remove", callback_data=f"rm:{item_id}")]])
