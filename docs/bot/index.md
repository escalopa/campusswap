# Telegram bot

The CampusSwap bot is a working version of the product inside Telegram, where students already chat. It follows the same flows as the Figma design, so real students can use it and you get real usage data for the case study.

!!! tip "Why a bot first?"
    It's the fastest way to test the idea with real people (a Lean UX experiment): no app store, no install, and it runs on your laptop with one config file.

Try it: [@campusswap_bot](https://t.me/campusswap_bot). It answers only while the bot is running on the host computer.

## Features

| Feature | In the bot |
|---|---|
| Onboarding | `/start` with a welcome cover image, optional university email check, choose dorm building |
| Bot profile | Name, About, intro description, profile photo, `/` command suggestions and a Menu button (`--setup-profile`) |
| Post an item | Photo (optional), title, category, condition, Free / Swap / Sell + price, pickup spot, up to 4 time slots, preview and publish |
| Browse | One card at a time, items from your building first; filter by category or free only |
| Request | Pick one of the owner's time slots; owner gets your name, building and rating |
| Accept / decline | Owner accepts one request; others are declined automatically and notified |
| Handover | Both see the pickup details and a **Handed over** button; either can cancel |
| Ratings | Both rate the exchange 1–5 stars; ratings appear on future requests |
| My items / requests | See statuses, remove an item |
| Profile | Rating, items given and received, items saved from the trash |

## How it maps to the design

| Figma flow step | Bot |
|---|---|
| Onboard | `/start` → email (optional) → building |
| Discover | 🔎 Browse → category or "Free only" → cards |
| Evaluate | Card: photo, price tag, condition, pickup spot, times, owner and rating |
| Request + arrange pickup | 🙋 Request → choose a time slot |
| Handover | ✅ Handed over |
| Rate | ⭐ 1–5 |
| Post (flow 2) | ➕ Post an item |

Next: [run it locally](setup.md).
