import asyncio

import os

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

import config
import database
from handlers import start, auth, download

logging.basicConfig(level=logging.INFO)

async def main():
    os.makedirs(config.SESSION_DIR, exist_ok=True)
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Clean dangling data files on boot
    for f in os.listdir(config.DATA_DIR):
        file_path = os.path.join(config.DATA_DIR, f)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except:
                pass
                
    await database.init_db()
    
    if not config.BOT_TOKEN:
        print("Error: BOT_TOKEN is not set in .env")
        return
        
    bot = Bot(token=config.BOT_TOKEN)
    await bot.set_my_commands([
        BotCommand(command="start", description="Bosh menyu")
    ])
    
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
