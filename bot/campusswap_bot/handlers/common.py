"""Shared helpers for handlers."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .. import keyboards
from ..config import Config
from ..db import Database, User


def db(context: ContextTypes.DEFAULT_TYPE) -> Database:
    return context.bot_data["db"]


def cfg(context: ContextTypes.DEFAULT_TYPE) -> Config:
    return context.bot_data["config"]


def is_onboarded(user: User | None, config: Config) -> bool:
    if user is None or not user.building:
        return False
    return not config.require_email or bool(user.email)


async def require_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> User | None:
    """Return the registered user, or tell them to run /start first."""
    tg = update.effective_user
    user = db(context).get_user(tg.id) if tg else None
    if is_onboarded(user, cfg(context)):
        # keep username / name fresh
        return db(context).upsert_user(tg.id, tg.username, tg.first_name)
    if update.callback_query:
        await update.callback_query.answer("Please send /start first.", show_alert=True)
    elif update.effective_message:
        await update.effective_message.reply_text("Please send /start to set up your profile first.")
    return None


async def send_menu(update: Update, text: str) -> None:
    await update.effective_message.reply_html(text, reply_markup=keyboards.main_menu())
