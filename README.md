# PrivateDownloader

A Telegram bot made using Aiogram 3 and Pyrogram that acts as a userbot to download media from private channels.

## Requirements
- Python 3.10+
- `aiogram`
- `pyrogram`
- `aiosqlite`
- `python-dotenv`

## Setup
1. Clone the repository.
2. Create `venv` and install requirements `pip install -r requirements.txt`.
3. Create a `.env` file with `BOT_TOKEN`, `API_ID`, and `API_HASH`.
4. Run the bot: `python3 main.py`.

## Features
- Multi-user authentication with 2FA support and reverse code safety feature.
- Secure database mapping for individual users.
- Fast downloads via localized userbot session tracking.

Made with ❤️ by uzbtrust
