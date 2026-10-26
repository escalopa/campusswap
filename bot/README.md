# CampusSwap Telegram bot

Students give away, swap or sell dorm items and agree on pickup, inside Telegram.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp config.example.toml config.toml   # paste your token from @BotFather
python -m campusswap_bot --config config.toml
```

Run the tests with `pip install -e ".[dev]" && pytest`.

Full documentation: [setup](https://escalopa.github.io/campusswap/bot/setup/) · [user guide](https://escalopa.github.io/campusswap/bot/user-guide/) · [architecture](https://escalopa.github.io/campusswap/bot/architecture/)
