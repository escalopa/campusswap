"""Webhook server for Cloud Run: python -m campusswap_bot.server --config config.cloud.toml

Telegram POSTs each update to /telegram with the secret in the X-Telegram-Bot-Api-Secret-Token header
(not in the URL, so it never shows up in request logs). The update is processed *inside* the request, so
Cloud Run's request-only CPU is enough, and the instance can scale to zero between messages.
Conversation state and drafts are saved to Firestore after every update (see persistence.py).
Run with max-instances=1 so one instance owns the in-memory conversation state.
"""

from __future__ import annotations

import argparse
import contextlib
import hmac
import logging
import os

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update

from .app import build_application, open_database
from .config import Config, load_config

log = logging.getLogger(__name__)


def create_app(config: Config) -> Starlette:
    if not config.webhook_secret:
        raise SystemExit("Set CAMPUSSWAP_WEBHOOK_SECRET (or [webhook].secret) for webhook mode.")
    db = open_database(config)
    persistence = None
    if config.backend == "firestore":
        from .persistence import FirestorePersistence

        persistence = FirestorePersistence(db.client)
    tg = build_application(config, db=db, persistence=persistence, webhook=True)
    secret = config.webhook_secret

    @contextlib.asynccontextmanager
    async def lifespan(_app):
        await tg.initialize()
        if tg.post_init:
            await tg.post_init(tg)
        await tg.start()
        yield
        await tg.stop()
        await tg.shutdown()

    async def telegram(request: Request) -> Response:
        if not hmac.compare_digest(request.headers.get("x-telegram-bot-api-secret-token", ""), secret):
            return Response(status_code=403)
        try:
            update = Update.de_json(await request.json(), tg.bot)
            await tg.process_update(update)
            await tg.update_persistence()
        except Exception:  # noqa: BLE001 - always answer 200 so Telegram doesn't retry forever
            log.exception("Failed to process update")
        return Response(status_code=200)

    async def health(_request: Request) -> Response:
        return PlainTextResponse("ok")

    return Starlette(routes=[Route("/telegram", telegram, methods=["POST"]), Route("/", health)],
                     lifespan=lifespan)


def main() -> None:
    parser = argparse.ArgumentParser(prog="campusswap_bot.server")
    parser.add_argument("--config", default="config.toml")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # request URLs contain the bot token
    uvicorn.run(create_app(load_config(args.config)), host="0.0.0.0", port=int(os.environ.get("PORT", "8080")),
                log_level="warning", access_log=False)


if __name__ == "__main__":
    main()
