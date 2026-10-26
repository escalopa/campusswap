"""End-to-end flows through the real handlers, with Telegram's network replaced by a fake.

Two students (Bob gives, Alice gets) go through onboarding, posting, browsing, requesting,
accepting, handover and rating. Every Bot API call is recorded so the tests can check what
each student would see.
"""

from __future__ import annotations

import asyncio
import itertools

import pytest
from telegram import Update
from telegram.ext import ExtBot

from campusswap_bot import texts
from campusswap_bot.app import build_application
from campusswap_bot.config import Config

BOT_USER = {"id": 999, "is_bot": True, "first_name": "CampusSwap", "username": "campusswap_test_bot"}


class FakeBot(ExtBot):
    """Records Bot API calls and returns minimal valid responses instead of calling Telegram."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(self, "calls", [])
        object.__setattr__(self, "_ids", itertools.count(1000))

    async def _do_post(self, endpoint, data, **kwargs):
        markup = data.get("reply_markup")
        if markup is not None and hasattr(markup, "to_dict"):
            markup = markup.to_dict()
        self.calls.append({
            "method": endpoint,
            "chat_id": data.get("chat_id"),
            "text": data.get("text") or data.get("caption") or "",
            "markup": markup,
            "show_alert": data.get("show_alert"),
            "alert": data.get("text") if endpoint == "answerCallbackQuery" else None,
        })
        if endpoint == "getMe":
            return BOT_USER
        if endpoint in {"sendMessage", "sendPhoto", "editMessageText", "editMessageCaption", "editMessageReplyMarkup"}:
            msg = {"message_id": next(self._ids), "date": 0, "chat": {"id": data.get("chat_id") or 0, "type": "private"},
                   "from": BOT_USER}
            if endpoint == "sendPhoto":
                msg["photo"] = [{"file_id": "WELCOME_OR_ITEM_PHOTO", "file_unique_id": "u", "width": 1, "height": 1}]
                msg["caption"] = data.get("caption", "")
            else:
                msg["text"] = data.get("text", "")
            return msg
        return True


USERS = {
    "bob": {"id": 202, "is_bot": False, "first_name": "Bob", "username": "bob"},
    "alice": {"id": 101, "is_bot": False, "first_name": "Alice", "username": "alice"},
    "carol": {"id": 303, "is_bot": False, "first_name": "Carol"},
}


class Harness:
    def __init__(self, tmp_path):
        self.bot = FakeBot("123456:TEST")
        self.config = Config(token="123456:TEST", database=tmp_path / "flows.db",
                             buildings=["Building 1", "Building 2", "Building 3"])
        self.app = build_application(self.config, bot=self.bot)
        self.db = self.app.bot_data["db"]
        self._uid = itertools.count(1)

    async def __aenter__(self):
        await self.app.initialize()
        return self

    async def __aexit__(self, *exc):
        await self.app.shutdown()

    async def _process(self, payload):
        self.bot.calls.clear()
        await self.app.process_update(Update.de_json(payload, self.bot))
        return list(self.bot.calls)

    async def say(self, who, text):
        user = USERS[who]
        n = next(self._uid)
        msg = {"message_id": n, "date": 0, "chat": {"id": user["id"], "type": "private"}, "from": user, "text": text}
        if text.startswith("/"):
            msg["entities"] = [{"type": "bot_command", "offset": 0, "length": len(text.split()[0])}]
        return await self._process({"update_id": n, "message": msg})

    async def photo(self, who):
        user = USERS[who]
        n = next(self._uid)
        msg = {"message_id": n, "date": 0, "chat": {"id": user["id"], "type": "private"}, "from": user,
               "photo": [{"file_id": "LAMP_PHOTO", "file_unique_id": "lp", "width": 640, "height": 640}]}
        return await self._process({"update_id": n, "message": msg})

    async def tap(self, who, data):
        user = USERS[who]
        n = next(self._uid)
        message = {"message_id": 5000 + n, "date": 0, "chat": {"id": user["id"], "type": "private"}, "from": BOT_USER, "text": "…"}
        return await self._process({"update_id": n, "callback_query": {
            "id": str(n), "from": user, "chat_instance": "ci", "data": data, "message": message}})


def to(calls, who, method=None):
    uid = USERS[who]["id"]
    return [c for c in calls if c["chat_id"] == uid and (method is None or c["method"] == method)]


def texts_to(calls, who):
    return "\n".join(c["text"] for c in to(calls, who))


def buttons(call):
    m = call["markup"] or {}
    return [b["callback_data"] for row in m.get("inline_keyboard", []) for b in row]


def alert(calls):
    return next((c["alert"] for c in calls if c["method"] == "answerCallbackQuery" and c["show_alert"]), None)


async def onboard(h, who, building_idx):
    calls = await h.say(who, "/start")
    assert to(calls, who, "sendPhoto"), "welcome image is sent on first /start"
    assert "Welcome to CampusSwap" in texts_to(calls, who)
    assert any(d.startswith("bld:") for c in to(calls, who) for d in buttons(c))
    calls = await h.tap(who, f"bld:{building_idx}")
    assert "You're all set" in texts_to(calls, who)


async def post_lamp(h):
    assert "Send a photo" in texts_to(await h.say("bob", "/post"), "bob")
    assert "What is it?" in texts_to(await h.photo("bob"), "bob")
    calls = await h.say("bob", "Desk lamp, IKEA")
    assert "category" in texts_to(calls, "bob")
    await h.tap("bob", "cat:1")
    await h.tap("bob", "cond:1")
    calls = await h.tap("bob", "kind:free")
    assert "spot:default" in [d for c in to(calls, "bob") for d in buttons(c)]
    calls = await h.tap("bob", "spot:default")
    assert "time slots" in texts_to(calls, "bob")
    calls = await h.say("bob", "Today 18:00, Tomorrow 12:00")
    preview = to(calls, "bob", "sendPhoto")
    assert preview and "Desk lamp, IKEA" in preview[0]["text"] and "Building 2 lobby" in preview[0]["text"]
    calls = await h.tap("bob", "pub:yes")
    assert "Published" in texts_to(calls, "bob")


async def post_kettle(h):
    await h.say("bob", "/post")
    await h.say("bob", "/skip")
    await h.say("bob", "Electric kettle")
    await h.tap("bob", "cat:0")
    await h.tap("bob", "cond:2")
    assert "Price" in texts_to(await h.tap("bob", "kind:sell"), "bob")
    assert "whole number" in texts_to(await h.say("bob", "cheap"), "bob")  # validation
    await h.say("bob", "150")
    await h.say("bob", "B2 kitchen")
    calls = await h.say("bob", "Tonight 20:00")
    assert "150 ₽" in texts_to(calls, "bob")
    await h.tap("bob", "pub:yes")


def test_full_exchange(tmp_path):
    async def run():
        async with Harness(tmp_path) as h:
            await onboard(h, "bob", 1)    # Building 2
            await onboard(h, "alice", 0)  # Building 1
            await post_lamp(h)
            await post_kettle(h)
            lamp, kettle = h.db.items_of(202)[1], h.db.items_of(202)[0]
            assert lamp.photo_file_id == "LAMP_PHOTO" and lamp.kind == "free" and lamp.slots == ["Today 18:00", "Tomorrow 12:00"]
            assert kettle.kind == "sell" and kettle.price == 150 and kettle.pickup_spot == "B2 kitchen"

            # Browse: newest first, navigation and the free-only filter
            assert "What are you looking for?" in texts_to(await h.say("alice", texts.BTN_BROWSE), "alice")
            calls = await h.tap("alice", "nav:a:0:0")
            assert "Electric kettle" in texts_to(calls, "alice") and "1 of 2" in texts_to(calls, "alice")
            calls = await h.tap("alice", "nav:a:0:1")
            card = to(calls, "alice", "sendPhoto")[0]
            assert "Desk lamp, IKEA" in card["text"] and f"req:{lamp.id}" in buttons(card)
            calls = await h.tap("alice", "nav:a:1:0")
            assert "Desk lamp" in texts_to(calls, "alice") and "kettle" not in texts_to(calls, "alice")
            assert "No items" in texts_to(await h.tap("bob", "nav:a:0:0"), "bob")  # own items are hidden

            # Request with a time slot; the owner is notified
            calls = await h.tap("alice", f"req:{lamp.id}")
            assert f"slot:{lamp.id}:0" in buttons(to(calls, "alice")[0])
            calls = await h.tap("alice", f"slot:{lamp.id}:0")
            assert "Request sent" in texts_to(calls, "alice")
            owner_msg = to(calls, "bob")[0]
            assert "Alice" in owner_msg["text"] and "Today 18:00" in owner_msg["text"]
            req_id = h.db.requests_of(101)[0].id
            assert buttons(owner_msg) == [f"acc:{req_id}", f"dec:{req_id}"]
            assert "already requested" in alert(await h.tap("alice", f"req:{lamp.id}"))

            # Only the owner can accept
            assert "not yours" in alert(await h.tap("alice", f"acc:{req_id}"))
            calls = await h.tap("bob", f"acc:{req_id}")
            assert "accepted your request" in texts_to(calls, "alice")
            assert h.db.get_item(lamp.id).status == "reserved"
            assert "No free items" in texts_to(await h.tap("alice", "nav:a:1:0"), "alice")  # reserved = hidden

            # Handover and ratings
            calls = await h.tap("alice", f"done:{req_id}")
            assert h.db.get_item(lamp.id).status == "given"
            assert h.db.get_request(req_id).status == "completed"
            assert any(d.startswith(f"rate:{req_id}:") for c in to(calls, "alice") for d in buttons(c))
            assert any(d.startswith(f"rate:{req_id}:") for c in to(calls, "bob") for d in buttons(c))
            assert "already" in alert(await h.tap("bob", f"done:{req_id}"))
            await h.tap("alice", f"rate:{req_id}:5")
            await h.tap("bob", f"rate:{req_id}:4")
            assert "already rated" in alert(await h.tap("alice", f"rate:{req_id}:1"))

            # Profile, my requests, my items, remove
            profile = texts_to(await h.say("bob", "/profile"), "bob")
            assert "⭐ 5.0 (1)" in profile and "Items given: 1" in profile
            assert "completed" in texts_to(await h.say("alice", "/myrequests"), "alice")
            calls = await h.say("bob", texts.BTN_MY_ITEMS)
            assert f"rm:{kettle.id}" in [d for c in to(calls, "bob") for d in buttons(c)]
            await h.tap("bob", f"rm:{kettle.id}")
            assert h.db.get_item(kettle.id).status == "removed"

    asyncio.run(run())


def test_decline_cancel_and_guards(tmp_path):
    async def run():
        async with Harness(tmp_path) as h:
            # Not registered yet
            assert "send /start" in texts_to(await h.say("carol", "/browse"), "carol")

            await onboard(h, "bob", 1)
            await onboard(h, "alice", 0)
            await post_lamp(h)
            lamp = h.db.items_of(202)[0]

            # Decline
            await h.tap("alice", f"req:{lamp.id}")
            await h.tap("alice", f"slot:{lamp.id}:1")
            req = h.db.requests_of(101)[0]
            calls = await h.tap("bob", f"dec:{req.id}")
            assert "can't give you" in texts_to(calls, "alice")
            assert h.db.get_request(req.id).status == "declined"

            # Request again, accept, then cancel the pickup: the item is available again
            await h.tap("alice", f"req:{lamp.id}")
            await h.tap("alice", f"slot:{lamp.id}:0")
            req2 = h.db.requests_of(101)[0]
            await h.tap("bob", f"acc:{req2.id}")
            calls = await h.tap("bob", f"cxl:{req2.id}")
            assert "cancelled" in texts_to(calls, "alice")
            assert h.db.get_item(lamp.id).status == "active"

            # Pressing a menu button in the middle of posting cancels the post and opens that menu
            await h.say("bob", "/post")
            calls = await h.say("bob", texts.BTN_BROWSE)
            out = texts_to(calls, "bob")
            assert "Cancelled" in out and "What are you looking for?" in out

            # Returning user: /start opens the menu without the welcome image
            calls = await h.say("alice", "/start")
            assert not to(calls, "alice", "sendPhoto") and "You're all set" in texts_to(calls, "alice")

    asyncio.run(run())


@pytest.mark.parametrize("domains,email,ok", [(["uni.edu"], "a@uni.edu", True), (["uni.edu"], "a@gmail.com", False)])
def test_email_step(tmp_path, domains, email, ok):
    async def run():
        h = Harness(tmp_path)
        h.app.bot_data["config"] = Config(token="1:T", database=tmp_path / "x.db", buildings=["B1"],
                                          university_email_domains=domains)
        async with h:
            calls = await h.say("alice", "/start")
            assert "university email" in texts_to(calls, "alice")
            calls = await h.say("alice", email)
            assert ("Which dorm building" in texts_to(calls, "alice")) is ok

    asyncio.run(run())
