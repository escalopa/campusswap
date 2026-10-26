"""Build the Telegram application and register all handlers."""

from __future__ import annotations

import logging
import warnings

from telegram import Bot, Update
from telegram.ext import Application, ContextTypes
from telegram.warnings import PTBUserWarning

from .config import Config
from .db import Database
from .handlers import account, browse, exchange, onboarding, post
from .profile import apply_commands

log = logging.getLogger(__name__)

# Conversations mix message and button steps on purpose; PTB warns about per_message tracking.
warnings.filterwarnings("ignore", message=r".*per_message.*", category=PTBUserWarning)



async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Unhandled error while processing an update", exc_info=context.error)
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(update.effective_chat.id, "😕 Something went wrong. Please try again.")
        except Exception:  # noqa: BLE001 - best effort only
            pass


async def _post_init(app: Application) -> None:
    await apply_commands(app.bot)
    me = await app.bot.get_me()
    log.info("CampusSwap bot is running as @%s. Press Ctrl+C to stop.", me.username)


def build_application(config: Config, bot: Bot | None = None) -> Application:
    builder = Application.builder().post_init(_post_init)
    builder = builder.bot(bot) if bot is not None else builder.token(config.token)
    app = builder.build()
    app.bot_data["config"] = config
    app.bot_data["db"] = Database(config.database)

    # Group 0: conversations (onboarding, posting). Group 1: menu buttons, browsing and exchange buttons.
    # A menu button pressed in the middle of posting cancels the post (group 0) and still opens that menu (group 1).
    for h in onboarding.handlers() + post.handlers():
        app.add_handler(h, group=0)
    for h in browse.handlers() + exchange.handlers() + account.handlers():
        app.add_handler(h, group=1)
    app.add_error_handler(_on_error)
    return app
