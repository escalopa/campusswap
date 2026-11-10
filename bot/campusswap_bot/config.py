"""Load and validate the bot configuration from a TOML file.

Secrets can also come from environment variables, which is how the bot runs on Cloud Run:
  CAMPUSSWAP_TOKEN           overrides [telegram].token
  CAMPUSSWAP_WEBHOOK_SECRET  overrides [webhook].secret
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CATEGORIES = [
    "Kitchen",
    "Lamps & electronics",
    "Furniture & storage",
    "Bedding",
    "Books",
    "Sports",
    "Clothes",
    "Other",
]

BACKENDS = ("sqlite", "firestore")


class ConfigError(ValueError):
    """Raised when the configuration file is missing or invalid."""


@dataclass(frozen=True)
class Config:
    token: str
    database: Path
    buildings: list[str]
    categories: list[str] = field(default_factory=lambda: list(DEFAULT_CATEGORIES))
    university_email_domains: list[str] = field(default_factory=list)
    max_slots: int = 4
    backend: str = "sqlite"
    firestore_project: str | None = None
    firestore_database: str = "(default)"
    webhook_secret: str | None = None

    @property
    def require_email(self) -> bool:
        return bool(self.university_email_domains)


def load_config(path: str | Path) -> Config:
    path = Path(path)
    if not path.is_file():
        raise ConfigError(
            f"Config file not found: {path}. Copy config.example.toml to config.toml and fill it in."
        )
    with path.open("rb") as f:
        try:
            raw = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ConfigError(f"Invalid TOML in {path}: {e}") from e

    token = os.environ.get("CAMPUSSWAP_TOKEN") or str(raw.get("telegram", {}).get("token", "")).strip()
    if not token or token.startswith("PASTE_"):
        raise ConfigError("Set [telegram].token in the config file (get one from @BotFather).")
    if ":" not in token:
        raise ConfigError("[telegram].token does not look like a bot token (expected '<id>:<secret>').")

    app = raw.get("app", {})
    buildings = [str(b).strip() for b in app.get("buildings", []) if str(b).strip()]
    if not buildings:
        raise ConfigError("Set at least one entry in [app].buildings.")
    categories = [str(c).strip() for c in app.get("categories", DEFAULT_CATEGORIES) if str(c).strip()]
    if not categories:
        raise ConfigError("[app].categories must not be empty.")
    domains = [str(d).strip().lower().lstrip("@") for d in app.get("university_email_domains", []) if str(d).strip()]
    max_slots = int(app.get("max_slots", 4))
    if not 1 <= max_slots <= 8:
        raise ConfigError("[app].max_slots must be between 1 and 8.")

    database = Path(app.get("database", "campusswap.db"))
    if not database.is_absolute():
        database = path.parent / database

    storage = raw.get("storage", {})
    backend = str(storage.get("backend", "sqlite")).strip().lower()
    if backend not in BACKENDS:
        raise ConfigError(f"[storage].backend must be one of {', '.join(BACKENDS)}.")

    webhook_secret = os.environ.get("CAMPUSSWAP_WEBHOOK_SECRET") or raw.get("webhook", {}).get("secret") or None

    return Config(
        token=token,
        database=database,
        buildings=buildings,
        categories=categories,
        university_email_domains=domains,
        max_slots=max_slots,
        backend=backend,
        firestore_project=storage.get("firestore_project") or None,
        firestore_database=storage.get("firestore_database") or "(default)",
        webhook_secret=webhook_secret,
    )
