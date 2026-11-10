"""Bot profile: name, descriptions, command suggestions, menu button and profile photo."""

from __future__ import annotations

from pathlib import Path

from telegram import Bot, BotCommand, InputProfilePhotoStatic, MenuButtonCommands

ASSETS = Path(__file__).parent / "assets"
AVATAR = ASSETS / "avatar.png"
WELCOME_IMAGE = ASSETS / "welcome.png"

NAME = "CampusSwap"

# Shown on the bot's profile page and in shared links (max 120 characters).
SHORT_DESCRIPTION = "Give away, swap or sell dorm items to students nearby. Pickup time and place built in. 🌱"

# Shown in an empty chat before the user taps Start (max 512 characters).
DESCRIPTION = (
    "♻️ CampusSwap helps students pass on dorm items: kettles, lamps, books, furniture and more.\n\n"
    "🔎 Browse items from your building first\n"
    "➕ Post an item in under a minute\n"
    "🆓 Give away, swap or sell\n"
    "🕒 Agree on a pickup time right in the chat\n"
    "⭐ Rate each other to build trust\n\n"
    "Tap Start to set up your profile."
)

# Suggestions shown when a user types "/" and in the menu button.
COMMANDS = [
    BotCommand("start", "Set up or open the menu"),
    BotCommand("browse", "Browse items"),
    BotCommand("post", "Post an item"),
    BotCommand("myitems", "Items you posted"),
    BotCommand("myrequests", "Items you requested"),
    BotCommand("profile", "Your rating and stats"),
    BotCommand("building", "Change your dorm building"),
    BotCommand("help", "How CampusSwap works"),
    BotCommand("cancel", "Cancel the current step"),
]

assert len(SHORT_DESCRIPTION) <= 120 and len(DESCRIPTION) <= 512


async def apply_commands(bot: Bot) -> None:
    await bot.set_my_commands(COMMANDS)
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def apply_profile(bot: Bot, with_photo: bool = True, name: str = NAME) -> list[str]:
    """Set everything Telegram shows about the bot. Only changes what differs (setMyName is rate-limited)."""
    done: list[str] = []
    if (await bot.get_my_name()).name != name:
        await bot.set_my_name(name)
        done.append(f"name → {name}")
    if (await bot.get_my_short_description()).short_description != SHORT_DESCRIPTION:
        await bot.set_my_short_description(SHORT_DESCRIPTION)
        done.append("short description (About) updated")
    if (await bot.get_my_description()).description != DESCRIPTION:
        await bot.set_my_description(DESCRIPTION)
        done.append("description (empty-chat intro) updated")
    await apply_commands(bot)
    done.append(f"{len(COMMANDS)} command suggestions + menu button set")
    if with_photo:
        with AVATAR.open("rb") as f:
            await bot.set_my_profile_photo(InputProfilePhotoStatic(f.read()))
        done.append("profile photo uploaded")
    return done
