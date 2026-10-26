"""Load and validate the bot configuration from a TOML file."""

from __future__ import annotations

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

    token = str(raw.get("telegram", {}).get("token", "")).strip()
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

    return Config(
        token=token,
        database=database,
        buildings=buildings,
        categories=categories,
        university_email_domains=domains,
        max_slots=max_slots,
    )
