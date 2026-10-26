"""Run the bot locally: python -m campusswap_bot --config config.toml"""

from __future__ import annotations

import argparse
import logging
import sys

from telegram import Update

from .app import build_application
from .config import ConfigError, load_config


def main() -> int:
    parser = argparse.ArgumentParser(prog="campusswap_bot", description="Run the CampusSwap Telegram bot (long polling).")
    parser.add_argument("--config", default="config.toml", help="path to the TOML config file (default: config.toml)")
    parser.add_argument("--debug", action="store_true", help="verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    # httpx logs every request URL, and Telegram URLs contain the bot token. Keep it out of the logs.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    try:
        config = load_config(args.config)
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 2

    app = build_application(config)
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
