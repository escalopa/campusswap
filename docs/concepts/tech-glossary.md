# Tech glossary

The terms behind the [CampusSwap Telegram bot](../bot/index.md) and this repository.

## Telegram bots

Telegram Bot API
:   Telegram's HTTP interface for bots. A bot is a special Telegram account controlled by a program instead of a person.

@BotFather
:   The official Telegram bot that creates other bots. Send it `/newbot`, choose a name and a username ending in `bot`, and it gives you a token.

Bot token
:   The password of your bot, like `123456789:AA…`. Anyone with it can control the bot, so keep it in `config.toml` (ignored by Git) and never share it. If it leaks, use `/revoke` in @BotFather.

Update
:   Anything that happens to the bot: a new message, a button tap, a photo. The bot program receives updates and reacts to them.

Long polling
:   The bot keeps asking Telegram "anything new?" and gets updates as they arrive. Works from any laptop with no server setup. CampusSwap uses this.

Webhook
:   The opposite: Telegram sends updates to a public HTTPS address. Needed for serverless hosting (for example Google Cloud Run), but not for running locally.

Handler
:   A function that reacts to one type of update, for example the `/start` command or a tap on a "Request" button.

Conversation handler
:   A multi-step dialog with states. Posting an item is one: photo → title → category → condition → free/swap/sell → price → spot → time slots → publish.

Inline keyboard
:   Buttons attached to a message (like "✅ Accept / ❌ Decline"). Tapping one sends a *callback query* to the bot.

Callback data
:   A short hidden string attached to an inline button (max 64 bytes), like `acc:42`, so the bot knows which button and which request was tapped.

Reply keyboard
:   The menu buttons shown instead of the phone keyboard ("🔎 Browse", "➕ Post an item").

file_id
:   Telegram stores uploaded photos and gives the bot a `file_id`. The bot saves that ID, not the photo itself, and reuses it to show the photo again.

## Python

Python
:   The programming language of the bot (version 3.11 or newer).

python-telegram-bot (PTB)
:   A popular open-source Python library that wraps the Telegram Bot API. It handles polling, handlers and conversations.

async / await
:   Python's way of waiting for slow things (network calls) without blocking the whole program. Every handler is an `async def` function.

Virtual environment (venv)
:   A private folder of Python packages for one project, so projects don't conflict. Created with `python3 -m venv .venv`.

pip
:   Python's package installer. `pip install -e .` installs the bot and its dependencies from `pyproject.toml`.

pyproject.toml
:   The project's metadata file: name, version, dependencies and test settings.

pytest
:   The test framework. `pytest` runs the automated tests in `bot/tests/`.

## Data and configuration

SQLite
:   A small database stored in a single file (`campusswap.db`). No server needed. It's built into Python.

Schema
:   The structure of the database: tables (users, items, requests, ratings), their columns and rules.

TOML
:   A simple, readable configuration format (`key = "value"`, `[sections]`). The bot reads `config.toml`.

Environment vs config file
:   Secrets can live in environment variables or in a config file. CampusSwap uses a git-ignored config file because it's the simplest for local use.

## Repository and docs

Git
:   Version control: it records every change to the project so you can see history and undo mistakes.

GitHub
:   A website that hosts Git repositories, with issues, pull requests and automation.

Repository (repo)
:   The project folder tracked by Git: code, docs and history.

Commit
:   A saved snapshot of changes with a message describing them.

Markdown
:   A simple text format for documents (`# Heading`, `**bold**`, `- list`). This whole site is written in Markdown.

MkDocs and Material for MkDocs
:   A tool that turns Markdown files into a documentation website, and the theme that gives it its look, search and dark mode.

GitHub Actions
:   GitHub's automation. On every push, our workflows run the bot tests and rebuild this site.

GitHub Pages
:   Free website hosting from a GitHub repository. This documentation is published there.

Mermaid
:   A way to write diagrams (flowcharts, sequences, data models) as text inside Markdown.

## Hosting (later)

Google Cloud Run
:   A Google Cloud service that runs a container and scales to zero when idle. A good home for the bot later, using a webhook instead of polling.

Cloud SQL / Firestore
:   Managed databases on Google Cloud, the next step after SQLite if the bot needs to run on a server.
