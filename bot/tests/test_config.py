import pytest

from campusswap_bot.config import ConfigError, load_config

VALID = """
[telegram]
token = "123456:ABC-DEF"

[app]
database = "data/test.db"
buildings = ["Building 1", "Building 2"]
university_email_domains = ["@Uni.edu"]
max_slots = 3
"""


def write(tmp_path, text):
    p = tmp_path / "config.toml"
    p.write_text(text)
    return p


def test_valid_config(tmp_path):
    cfg = load_config(write(tmp_path, VALID))
    assert cfg.token == "123456:ABC-DEF"
    assert cfg.buildings == ["Building 1", "Building 2"]
    assert cfg.university_email_domains == ["uni.edu"]
    assert cfg.require_email
    assert cfg.max_slots == 3
    assert cfg.database == tmp_path / "data/test.db"
    assert "Kitchen" in cfg.categories


def test_missing_file(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.toml")


def test_placeholder_token_rejected(tmp_path):
    with pytest.raises(ConfigError, match="token"):
        load_config(write(tmp_path, VALID.replace("123456:ABC-DEF", "PASTE_YOUR_BOT_TOKEN_HERE")))


def test_no_buildings_rejected(tmp_path):
    with pytest.raises(ConfigError, match="buildings"):
        load_config(write(tmp_path, VALID.replace('["Building 1", "Building 2"]', "[]")))


def test_email_step_optional(tmp_path):
    cfg = load_config(write(tmp_path, VALID.replace('["@Uni.edu"]', "[]")))
    assert not cfg.require_email
