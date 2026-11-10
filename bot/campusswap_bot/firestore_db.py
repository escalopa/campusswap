"""Firestore storage with the same interface as the SQLite `Database` (used on Cloud Run).

Collections: users, items, requests, ratings, counters. Items and requests keep small integer IDs
(from a transactional counter) because they appear in Telegram button callback data (max 64 bytes).
Queries use only equality filters, so no composite indexes are needed; ordering happens in Python,
which is fine for a campus pilot.
"""

from __future__ import annotations

from datetime import datetime, timezone

from google.api_core.exceptions import AlreadyExists
from google.cloud import firestore

from .db import Item, Request, Stats, User


def _now() -> datetime:
    return datetime.now(timezone.utc)


class FirestoreDatabase:
    def __init__(self, project: str | None = None, database: str = "(default)", prefix: str = "", credentials=None):
        self.client = firestore.Client(project=project, database=database, credentials=credentials)
        self.prefix = prefix  # lets tests isolate their data in a shared database

    def close(self) -> None:
        self.client.close()

    def _col(self, name: str):
        return self.client.collection(self.prefix + name)

    def _next_id(self, name: str) -> int:
        ref = self._col("counters").document(name)

        @firestore.transactional
        def bump(tx) -> int:
            snap = ref.get(transaction=tx)
            value = (snap.get("next") if snap.exists else 0) + 1
            tx.set(ref, {"next": value})
            return value

        return bump(self.client.transaction())

    # ---------- users
    def upsert_user(self, user_id: int, username: str | None, first_name: str) -> User:
        ref = self._col("users").document(str(user_id))
        ref.set({"id": user_id, "username": username, "first_name": first_name}, merge=True)
        snap = ref.get()
        if "created_at" not in (snap.to_dict() or {}):
            ref.update({"created_at": _now()})
        return self.get_user(user_id)  # type: ignore[return-value]

    def get_user(self, user_id: int) -> User | None:
        snap = self._col("users").document(str(user_id)).get()
        if not snap.exists:
            return None
        d = snap.to_dict()
        return User(d["id"], d.get("username"), d["first_name"], d.get("building"), d.get("email"))

    def set_building(self, user_id: int, building: str) -> None:
        self._col("users").document(str(user_id)).update({"building": building})

    def set_email(self, user_id: int, email: str) -> None:
        self._col("users").document(str(user_id)).update({"email": email})

    # ---------- items
    @staticmethod
    def _item(d: dict) -> Item:
        return Item(
            id=d["id"], owner_id=d["owner_id"], title=d["title"], category=d["category"], condition=d["condition"],
            kind=d["kind"], price=d.get("price"), pickup_spot=d["pickup_spot"], slots=list(d["slots"]),
            photo_file_id=d.get("photo_file_id"), status=d["status"],
        )

    def create_item(self, owner_id, title, category, condition, kind, price, pickup_spot, slots, photo_file_id) -> Item:
        item_id = self._next_id("items")
        self._col("items").document(str(item_id)).set({
            "id": item_id, "owner_id": owner_id, "title": title, "category": category, "condition": condition,
            "kind": kind, "price": price, "pickup_spot": pickup_spot, "slots": list(slots),
            "photo_file_id": photo_file_id, "status": "active", "created_at": _now(),
        })
        return self.get_item(item_id)  # type: ignore[return-value]

    def get_item(self, item_id: int) -> Item | None:
        snap = self._col("items").document(str(item_id)).get()
        return self._item(snap.to_dict()) if snap.exists else None

    def browse_items(self, viewer_id: int, viewer_building: str | None, category: str | None, free_only: bool) -> list[Item]:
        q = self._col("items").where(filter=firestore.FieldFilter("status", "==", "active"))
        if category:
            q = q.where(filter=firestore.FieldFilter("category", "==", category))
        if free_only:
            q = q.where(filter=firestore.FieldFilter("kind", "==", "free"))
        docs = [d.to_dict() for d in q.stream()]
        docs = [d for d in docs if d["owner_id"] != viewer_id]
        owners = {d["owner_id"] for d in docs}
        refs = [self._col("users").document(str(o)) for o in owners]
        building = {s.get("id"): (s.to_dict() or {}).get("building") for s in self.client.get_all(refs) if s.exists}
        # Same order as SQLite: viewer's building first, then newest first.
        docs.sort(key=lambda d: (building.get(d["owner_id"]) != viewer_building, -d["created_at"].timestamp(), -d["id"]))
        return [self._item(d) for d in docs]

    def items_of(self, owner_id: int) -> list[Item]:
        q = self._col("items").where(filter=firestore.FieldFilter("owner_id", "==", owner_id))
        docs = [d.to_dict() for d in q.stream()]
        return [self._item(d) for d in sorted(docs, key=lambda d: -d["id"]) if d["status"] != "removed"]

    def set_item_status(self, item_id: int, status: str) -> None:
        self._col("items").document(str(item_id)).update({"status": status})

    # ---------- requests
    @staticmethod
    def _request(d: dict) -> Request:
        return Request(d["id"], d["item_id"], d["requester_id"], d["slot"], d["status"])

    def create_request(self, item_id: int, requester_id: int, slot: str) -> Request:
        request_id = self._next_id("requests")
        now = _now()
        self._col("requests").document(str(request_id)).set({
            "id": request_id, "item_id": item_id, "requester_id": requester_id, "slot": slot,
            "status": "pending", "created_at": now, "updated_at": now,
        })
        return self.get_request(request_id)  # type: ignore[return-value]

    def get_request(self, request_id: int) -> Request | None:
        snap = self._col("requests").document(str(request_id)).get()
        return self._request(snap.to_dict()) if snap.exists else None

    def _requests_where(self, **eq) -> list[dict]:
        q = self._col("requests")
        for k, v in eq.items():
            q = q.where(filter=firestore.FieldFilter(k, "==", v))
        return [d.to_dict() for d in q.stream()]

    def open_request(self, item_id: int, requester_id: int) -> Request | None:
        for d in self._requests_where(item_id=item_id, requester_id=requester_id):
            if d["status"] in ("pending", "accepted"):
                return self._request(d)
        return None

    def pending_requests_for_item(self, item_id: int) -> list[Request]:
        return [self._request(d) for d in self._requests_where(item_id=item_id, status="pending")]

    def requests_of(self, requester_id: int) -> list[Request]:
        docs = sorted(self._requests_where(requester_id=requester_id), key=lambda d: -d["id"])[:20]
        return [self._request(d) for d in docs]

    def set_request_status(self, request_id: int, status: str) -> None:
        self._col("requests").document(str(request_id)).update({"status": status, "updated_at": _now()})

    # ---------- ratings & stats
    def add_rating(self, request_id: int, rater_id: int, ratee_id: int, stars: int) -> bool:
        ref = self._col("ratings").document(f"{request_id}_{rater_id}")
        try:
            ref.create({"request_id": request_id, "rater_id": rater_id, "ratee_id": ratee_id,
                        "stars": stars, "created_at": _now()})
        except AlreadyExists:
            return False
        return True

    def stats(self, user_id: int) -> Stats:
        stars = [d.get("stars") for d in self._col("ratings")
                 .where(filter=firestore.FieldFilter("ratee_id", "==", user_id)).stream()]
        given = sum(1 for _ in self._col("items").where(filter=firestore.FieldFilter("owner_id", "==", user_id))
                    .where(filter=firestore.FieldFilter("status", "==", "given")).stream())
        received = len(self._requests_where(requester_id=user_id, status="completed"))
        rating = round(sum(stars) / len(stars), 1) if stars else None
        return Stats(rating=rating, rating_count=len(stars), given=given, received=received)
