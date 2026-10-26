# Run the bot locally

The bot runs on your computer with **long polling**: no server, no public URL. It stops when you close the terminal.

## 1. Requirements

- Python **3.11 or newer** (`python3 --version`)
- A Telegram account

## 2. Create a bot and get a token

1. Open [@BotFather](https://t.me/BotFather) in Telegram and send `/newbot`.
2. Choose a display name (e.g. *CampusSwap*) and a username ending in `bot` (e.g. `campusswap_test_bot`).
3. BotFather replies with a **token** like `123456789:AA…`. Treat it like a password.

## 3. Install

```bash
git clone https://github.com/escalopa/campusswap.git
cd campusswap/bot
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 4. Configure

```bash
cp config.example.toml config.toml
```

Open `config.toml` and set at least the token and your dorm buildings:

```toml
[telegram]
token = "123456789:AA..."

[app]
database = "campusswap.db"
buildings = ["Building 1", "Building 2", "Building 3", "Building 4"]
university_email_domains = []   # e.g. ["university.edu"] to ask for a university email
max_slots = 4
```

!!! danger "Keep the token secret"
    `config.toml` is listed in `.gitignore`, so Git won't commit it. Never paste the token into code, issues or chats. If it leaks, send `/revoke` to @BotFather and update the config.

## 5. Run

```bash
python -m campusswap_bot --config config.toml
```

You should see `CampusSwap bot is running as @your_bot_username`. Open the bot in Telegram and send `/start`.

Stop it with ++ctrl+c++. Data stays in `campusswap.db`; delete that file to start fresh.

## Testing with two accounts

Exchanges need two people. Test with a friend, or use a second Telegram account: post an item from one account, request it from the other, accept, hand over and rate.

## Run the tests

```bash
pip install -e ".[dev]"
pytest
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Config error: Config file not found` | Run the command from the `bot/` folder, or pass the full path with `--config` |
| `Config error: Set [telegram].token` | Paste the token from @BotFather into `config.toml` |
| `telegram.error.InvalidToken` | The token is wrong or revoked; get a new one from @BotFather |
| `Conflict: terminated by other getUpdates request` | The bot is already running somewhere else; stop the other copy |
| The owner never gets requests | They must open the bot and send `/start` once, otherwise Telegram doesn't let the bot message them |
