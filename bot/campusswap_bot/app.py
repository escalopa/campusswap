"""Build the Telegram application and register all handlers."""

from __future__ import annotations

import logging
import warnings

from telegram import Bot, Update
from telegram.ext import Application, BasePersistence, ContextTypes
from telegram.error import NetworkError
from telegram.warnings import PTBUserWarning

from .config import Config
from .db import Database
from .handlers import account, browse, exchange, onboarding, post
from .profile import apply_commands

log = logging.getLogger(__name__)

# Conversations mix message and button steps on purpose; PTB warns about per_message tracking.
warnings.filterwarnings("ignore", message=r".*per_message.*", category=PTBUserWarning)



async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if isinstance(context.error, NetworkError):
        # Slow or flaky connection to api.telegram.org: PTB retries polling by itself.
        log.warning("Telegram network issue (%s); retrying", type(context.error).__name__)
        return
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


def open_database(config: Config):
    """SQLite for local runs, Firestore on Cloud Run."""
    if config.backend == "firestore":
        from .firestore_db import FirestoreDatabase

        return FirestoreDatabase(project=config.firestore_project, database=config.firestore_database)
    return Database(config.database)


def build_application(
    config: Config,
    bot: Bot | None = None,
    db=None,
    persistence: BasePersistence | None = None,
    webhook: bool = False,
) -> Application:
    builder = Application.builder().post_init(_post_init)
    if bot is not None:
        builder = builder.bot(bot)
    else:
        # Generous timeouts and a bigger pool: Telegram can be slow to reach on some networks.
        builder = (
            builder.token(config.token)
            .connect_timeout(30).read_timeout(30).write_timeout(30).pool_timeout(30).connection_pool_size(16)
            .get_updates_connect_timeout(30).get_updates_read_timeout(40).get_updates_pool_timeout(30)
        )
    if persistence is not None:
        builder = builder.persistence(persistence)
    if webhook:
        builder = builder.updater(None)  # updates arrive through our own HTTP endpoint
    app = builder.build()
    app.bot_data["config"] = config
    app.bot_data["db"] = db if db is not None else open_database(config)
    persistent = persistence is not None

    # Group 0: conversations (onboarding, posting). Group 1: menu buttons, browsing and exchange buttons.
    # A menu button pressed in the middle of posting cancels the post (group 0) and still opens that menu (group 1).
    for h in onboarding.handlers(persistent) + post.handlers(persistent):
        app.add_handler(h, group=0)
    for h in browse.handlers() + exchange.handlers() + account.handlers():
        app.add_handler(h, group=1)
    app.add_error_handler(_on_error)
    return app
