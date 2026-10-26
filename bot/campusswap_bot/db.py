"""SQLite storage for users, items, requests and ratings."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,          -- Telegram user id
    username    TEXT,
    first_name  TEXT NOT NULL,
    building    TEXT,
    email       TEXT,
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id      INTEGER NOT NULL REFERENCES users(id),
    title         TEXT NOT NULL,
    category      TEXT NOT NULL,
    condition     TEXT NOT NULL,
    kind          TEXT NOT NULL CHECK (kind IN ('free', 'swap', 'sell')),
    price         INTEGER,
    pickup_spot   TEXT NOT NULL,
    slots         TEXT NOT NULL,              -- JSON list of pickup time slots
    photo_file_id TEXT,
    status        TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'reserved', 'given', 'removed')),
    created_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS requests (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id      INTEGER NOT NULL REFERENCES items(id),
    requester_id INTEGER NOT NULL REFERENCES users(id),
    slot         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending', 'accepted', 'declined', 'cancelled', 'completed')),
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ratings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL REFERENCES requests(id),
    rater_id   INTEGER NOT NULL REFERENCES users(id),
    ratee_id   INTEGER NOT NULL REFERENCES users(id),
    stars      INTEGER NOT NULL CHECK (stars BETWEEN 1 AND 5),
    created_at TEXT NOT NULL,
    UNIQUE (request_id, rater_id)
);
CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
CREATE INDEX IF NOT EXISTS idx_requests_item ON requests(item_id);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class User:
    id: int
    username: str | None
    first_name: str
    building: str | None
    email: str | None


@dataclass(frozen=True)
class Item:
    id: int
    owner_id: int
    title: str
    category: str
    condition: str
    kind: str
    price: int | None
    pickup_spot: str
    slots: list[str]
    photo_file_id: str | None
    status: str


@dataclass(frozen=True)
class Request:
    id: int
    item_id: int
    requester_id: int
    slot: str
    status: str


@dataclass(frozen=True)
class Stats:
    rating: float | None
    rating_count: int
    given: int
    received: int


class Database:
    def __init__(self, path: str | Path):
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ---------- users
    def upsert_user(self, user_id: int, username: str | None, first_name: str) -> User:
        self.conn.execute(
            """INSERT INTO users (id, username, first_name, created_at) VALUES (?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET username = excluded.username, first_name = excluded.first_name""",
            (user_id, username, first_name, _now()),
        )
        self.conn.commit()
        return self.get_user(user_id)  # type: ignore[return-value]

    def get_user(self, user_id: int) -> User | None:
        row = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return None
        return User(row["id"], row["username"], row["first_name"], row["building"], row["email"])

    def set_building(self, user_id: int, building: str) -> None:
        self.conn.execute("UPDATE users SET building = ? WHERE id = ?", (building, user_id))
        self.conn.commit()

    def set_email(self, user_id: int, email: str) -> None:
        self.conn.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
        self.conn.commit()

    # ---------- items
    def create_item(
        self,
        owner_id: int,
        title: str,
        category: str,
        condition: str,
        kind: str,
        price: int | None,
        pickup_spot: str,
        slots: list[str],
        photo_file_id: str | None,
    ) -> Item:
        cur = self.conn.execute(
            """INSERT INTO items (owner_id, title, category, condition, kind, price, pickup_spot, slots,
                                  photo_file_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (owner_id, title, category, condition, kind, price, pickup_spot, json.dumps(slots), photo_file_id, _now()),
        )
        self.conn.commit()
        return self.get_item(cur.lastrowid)  # type: ignore[arg-type,return-value]

    @staticmethod
    def _item(row: sqlite3.Row) -> Item:
        return Item(
            id=row["id"],
            owner_id=row["owner_id"],
            title=row["title"],
            category=row["category"],
            condition=row["condition"],
            kind=row["kind"],
            price=row["price"],
            pickup_spot=row["pickup_spot"],
            slots=json.loads(row["slots"]),
            photo_file_id=row["photo_file_id"],
            status=row["status"],
        )

    def get_item(self, item_id: int) -> Item | None:
        row = self.conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return self._item(row) if row else None

    def browse_items(
        self, viewer_id: int, viewer_building: str | None, category: str | None, free_only: bool
    ) -> list[Item]:
        """Active items from other users. Items from the viewer's building come first, newest first."""
        sql = """SELECT i.* FROM items i JOIN users u ON u.id = i.owner_id
                 WHERE i.status = 'active' AND i.owner_id != ?"""
        params: list[object] = [viewer_id]
        if category:
            sql += " AND i.category = ?"
            params.append(category)
        if free_only:
            sql += " AND i.kind = 'free'"
        sql += " ORDER BY (u.building IS ?) DESC, i.created_at DESC, i.id DESC"
        params.append(viewer_building)
        return [self._item(r) for r in self.conn.execute(sql, params).fetchall()]

    def items_of(self, owner_id: int) -> list[Item]:
        rows = self.conn.execute(
            "SELECT * FROM items WHERE owner_id = ? AND status != 'removed' ORDER BY id DESC", (owner_id,)
        ).fetchall()
        return [self._item(r) for r in rows]

    def set_item_status(self, item_id: int, status: str) -> None:
        self.conn.execute("UPDATE items SET status = ? WHERE id = ?", (status, item_id))
        self.conn.commit()

    # ---------- requests
    @staticmethod
    def _request(row: sqlite3.Row) -> Request:
        return Request(row["id"], row["item_id"], row["requester_id"], row["slot"], row["status"])

    def create_request(self, item_id: int, requester_id: int, slot: str) -> Request:
        now = _now()
        cur = self.conn.execute(
            "INSERT INTO requests (item_id, requester_id, slot, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (item_id, requester_id, slot, now, now),
        )
        self.conn.commit()
        return self.get_request(cur.lastrowid)  # type: ignore[arg-type,return-value]

    def get_request(self, request_id: int) -> Request | None:
        row = self.conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
        return self._request(row) if row else None

    def open_request(self, item_id: int, requester_id: int) -> Request | None:
        row = self.conn.execute(
            "SELECT * FROM requests WHERE item_id = ? AND requester_id = ? AND status IN ('pending', 'accepted')",
            (item_id, requester_id),
        ).fetchone()
        return self._request(row) if row else None

    def pending_requests_for_item(self, item_id: int) -> list[Request]:
        rows = self.conn.execute(
            "SELECT * FROM requests WHERE item_id = ? AND status = 'pending'", (item_id,)
        ).fetchall()
        return [self._request(r) for r in rows]

    def requests_of(self, requester_id: int) -> list[Request]:
        rows = self.conn.execute(
            "SELECT * FROM requests WHERE requester_id = ? ORDER BY id DESC LIMIT 20", (requester_id,)
        ).fetchall()
        return [self._request(r) for r in rows]

    def set_request_status(self, request_id: int, status: str) -> None:
        self.conn.execute(
            "UPDATE requests SET status = ?, updated_at = ? WHERE id = ?", (status, _now(), request_id)
        )
        self.conn.commit()

    # ---------- ratings & stats
    def add_rating(self, request_id: int, rater_id: int, ratee_id: int, stars: int) -> bool:
        """Store a rating. Returns False if this user already rated this exchange."""
        try:
            self.conn.execute(
                "INSERT INTO ratings (request_id, rater_id, ratee_id, stars, created_at) VALUES (?, ?, ?, ?, ?)",
                (request_id, rater_id, ratee_id, stars, _now()),
            )
        except sqlite3.IntegrityError:
            return False
        self.conn.commit()
        return True

    def stats(self, user_id: int) -> Stats:
        r = self.conn.execute(
            "SELECT AVG(stars) AS avg, COUNT(*) AS n FROM ratings WHERE ratee_id = ?", (user_id,)
        ).fetchone()
        given = self.conn.execute(
            "SELECT COUNT(*) FROM items WHERE owner_id = ? AND status = 'given'", (user_id,)
        ).fetchone()[0]
        received = self.conn.execute(
            "SELECT COUNT(*) FROM requests WHERE requester_id = ? AND status = 'completed'", (user_id,)
        ).fetchone()[0]
        return Stats(rating=round(r["avg"], 1) if r["avg"] is not None else None, rating_count=r["n"],
                     given=given, received=received)
