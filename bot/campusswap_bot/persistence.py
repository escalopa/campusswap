"""Firestore persistence for conversation states and user_data (needed on Cloud Run).

Cloud Run can stop the instance between messages, so the step a user is at in "post an item" and the
draft they are filling in must be saved outside memory. bot_data is not persisted (it holds the config
and the database client), and neither is chat_data (unused).
"""

from __future__ import annotations

import json
from copy import deepcopy

from google.cloud import firestore
from telegram.ext import BasePersistence, PersistenceInput


class FirestorePersistence(BasePersistence):
    def __init__(self, client: firestore.Client, prefix: str = ""):
        super().__init__(store_data=PersistenceInput(bot_data=False, chat_data=False, user_data=True, callback_data=False),
                         update_interval=60)
        self.client = client
        self.prefix = prefix

    def _col(self, name: str):
        return self.client.collection(self.prefix + name)

    # ---------- user_data
    async def get_user_data(self) -> dict[int, dict]:
        return {int(d.id): (d.to_dict() or {}).get("data", {}) for d in self._col("ptb_user_data").stream()}

    async def update_user_data(self, user_id: int, data: dict) -> None:
        self._col("ptb_user_data").document(str(user_id)).set({"data": deepcopy(data)})

    async def drop_user_data(self, user_id: int) -> None:
        self._col("ptb_user_data").document(str(user_id)).delete()

    async def refresh_user_data(self, user_id: int, user_data: dict) -> None:
        pass  # a single instance (max-instances=1) owns the data, so memory is never stale

    # ---------- conversations
    async def get_conversations(self, name: str) -> dict:
        out = {}
        for d in self._col("ptb_conversations").where(filter=firestore.FieldFilter("name", "==", name)).stream():
            v = d.to_dict()
            out[tuple(json.loads(v["key"]))] = v["state"]
        return out

    async def update_conversation(self, name: str, key: tuple, new_state: object | None) -> None:
        ref = self._col("ptb_conversations").document(f"{name}:" + ":".join(str(k) for k in key))
        if new_state is None:
            ref.delete()
        else:
            ref.set({"name": name, "key": json.dumps(list(key)), "state": new_state})

    # ---------- not persisted
    async def get_bot_data(self) -> dict:
        return {}

    async def update_bot_data(self, data) -> None:
        pass

    async def refresh_bot_data(self, bot_data) -> None:
        pass

    async def get_chat_data(self) -> dict:
        return {}

    async def update_chat_data(self, chat_id: int, data) -> None:
        pass

    async def drop_chat_data(self, chat_id: int) -> None:
        pass

    async def refresh_chat_data(self, chat_id: int, chat_data) -> None:
        pass

    async def get_callback_data(self):
        return None

    async def update_callback_data(self, data) -> None:
        pass

    async def flush(self) -> None:
        pass
