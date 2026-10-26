from campusswap_bot.app import build_application
from campusswap_bot.config import Config


def test_application_builds_without_network(tmp_path):
    cfg = Config(token="123456:TEST", database=tmp_path / "t.db", buildings=["B1"])
    app = build_application(cfg)
    assert app.bot_data["config"] is cfg
    assert len(app.handlers[0]) >= 2 and len(app.handlers[1]) >= 10
