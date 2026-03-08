import os
import asyncio
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from states import DownloadState
import userbot_manager
from utils import is_valid_telegram_link, format_progress
import config

router = Router()

@router.message(DownloadState.waiting_for_link)
async def process_link(message: Message, state: FSMContext):
    link = message.text
    if not is_valid_telegram_link(link):
        await message.answer("❌ Bu to'g'ri Telegram linkiga o'xshamayapti.\n\nLink formati: https://t.me/c/123/456 yoki https://t.me/kanal/456")
        return
        
    data = await state.get_data()
    phone = data.get("selected_account")
    
    if not phone:
        await message.answer("❌ Akkaunt tanlanmagan. Iltimos, /start orqali akkauntdan birini tanlang.")
        await state.clear()
        return

    progress_msg = await message.answer("✅ Link qabul qilindi! Ma'lumot izlanmoqda va yuklashga tayyorlanmoqda, kuting... ⏳")
    
    bot_info = await message.bot.get_me()
    bot_username = bot_info.username

    last_down_perc = 0
    async def progress_down(current, total):
        nonlocal last_down_perc
        if total == 0: return
        perc = (current / total) * 100
        if perc - last_down_perc >= 5:
            last_down_perc = perc
            try:
                text = format_progress(current, total, prefix="📥 Data tortilmoqda:\n")
                await progress_msg.edit_text(text)
            except:
                pass

    last_up_perc = 0
    async def progress_up(current, total):
        nonlocal last_up_perc
        if total == 0: return
        perc = (current / total) * 100
        if perc - last_up_perc >= 5:
            last_up_perc = perc
            try:
                text = format_progress(current, total, prefix="📤 Sizga yuborilmoqda:\n")
                await progress_msg.edit_text(text)
            except:
                pass

    try:
        result = await userbot_manager.download_message_media(
            phone, link, bot_username, 
            progress_down=progress_down, 
            progress_up=progress_up
        )
        
        if not result.get("ok"):
            await progress_msg.edit_text(f"❌ Xatolik yuz berdi: {result.get('error')}")
            return
            
        await progress_msg.delete()
            
    except Exception as e:
        await progress_msg.edit_text(f"❌ Kutilmagan xatolik: {str(e)}")
