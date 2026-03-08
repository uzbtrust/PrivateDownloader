import asyncio

import os

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database
from handlers import start, auth, download

logging.basicConfig(level=logging.INFO)

async def main():
    os.makedirs(config.SESSION_DIR, exist_ok=True)
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    await database.reset_db()
    await database.init_db()
    
    if not config.BOT_TOKEN:
        print("Error: BOT_TOKEN is not set in .env")
        return
        
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(start.router)
    dp.include_router(auth.router)
    dp.include_router(download.router)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("Bot is running...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
