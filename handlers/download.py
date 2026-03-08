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
    
    last_perc = 0
    async def pyrogram_progress(current, total):
        nonlocal last_perc
        if total == 0: return
        perc = (current / total) * 100
        if perc - last_perc >= 10:
            last_perc = perc
            try:
                text = format_progress(current, total)
                await progress_msg.edit_text(f"⏳ Yuklanmoqda: {text}")
            except:
                pass

    try:
        result = await userbot_manager.download_message_media(phone, link, progress_callback=pyrogram_progress)
        
        if not result.get("ok"):
            await progress_msg.edit_text(f"❌ Xatolik yuz berdi: {result.get('error')}")
            return
            
        await progress_msg.edit_text("⏳ Fayl serverga olindi, endi sizga yuborilmoqda...")
        
        if result.get("type") == "text":
            await message.answer(result.get("text"))
            await progress_msg.delete()
        elif result.get("type") == "media":
            file_path = result.get("file_path")
            caption = result.get("caption") or ""
            
            input_file = FSInputFile(file_path)
            py_msg = result.get("message")
            
            try:
                if py_msg.photo:
                    await message.answer_photo(photo=input_file, caption=caption)
                elif py_msg.video:
                    await message.answer_video(video=input_file, caption=caption)
                elif py_msg.audio:
                    await message.answer_audio(audio=input_file, caption=caption)
                elif py_msg.document:
                    await message.answer_document(document=input_file, caption=caption)
                elif py_msg.voice:
                    await message.answer_voice(voice=input_file, caption=caption)
                elif py_msg.animation:
                    await message.answer_animation(animation=input_file, caption=caption)
                elif py_msg.sticker:
                    await message.answer_sticker(sticker=input_file)
                else:
                    await message.answer_document(document=input_file, caption=caption)
            except Exception as e:
                await message.answer(f"❌ Faylni yuborishda xatolik: {str(e)}")
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            await progress_msg.delete()
            
    except Exception as e:
        await progress_msg.edit_text(f"❌ Kutilmagan xatolik: {str(e)}")
