from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext

import database
from states import DownloadState

router = Router()

def get_accounts_keyboard(accounts):
    keyboard = []
    for acc in accounts:
        keyboard.append([InlineKeyboardButton(text=f"📱 {acc}", callback_data=f"select_acc_{acc}")])
    
    keyboard.append([InlineKeyboardButton(text="➕ Akkaunt qo'shish", callback_data="add_account")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    if phone:
        import userbot_manager
        await userbot_manager.disconnect_auth(phone)
        
    await state.clear()
    
    user_id = message.from_user.id
    accounts = await database.get_accounts(user_id)
    
    text = "👋 Assalomu alaykum! Userbot Downloaderga xush kelibsiz.\n\n"
    if not accounts:
        text += "Sizda hali akkauntlar yo'q. Iltimos, pastdagi tugma orqali akkaunt qo'shing."
    else:
        text += "Mavjud akkauntlaringizni tanlang yoki yangisini qo'shing."
        
    await message.answer(text, reply_markup=get_accounts_keyboard(accounts))

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    if phone:
        import userbot_manager
        await userbot_manager.disconnect_auth(phone)
        
    await state.clear()
    
    user_id = callback.from_user.id
    accounts = await database.get_accounts(user_id)
    
    text = "Bosh menyu. Akkauntni tanlang yoki yangisini qo'shing."
    await callback.message.edit_text(text, reply_markup=get_accounts_keyboard(accounts))

@router.callback_query(F.data.startswith("select_acc_"))
async def select_account(callback: CallbackQuery, state: FSMContext):
    phone = callback.data.replace("select_acc_", "")
    
    await state.update_data(selected_account=phone)
    await state.set_state(DownloadState.waiting_for_link)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        f"✅ Akkaunt tanlandi: {phone}\n\n"
        f"📥 Endi menga maxfiy yoki public kanal / guruhdan link yuboring (masalan: https://t.me/c/1234567/100)",
        reply_markup=keyboard
    )
