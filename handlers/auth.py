from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from states import AuthState
import userbot_manager

router = Router()

def cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="main_menu")]
    ])

@router.callback_query(F.data == "add_account")
async def add_account_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AuthState.waiting_for_phone)
    await callback.message.edit_text(
        "📞 Iltimos, telefon raqamingizni xalqaro formatda kiriting (masalan: +998901234567):",
        reply_markup=cancel_keyboard()
    )

@router.message(AuthState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.replace(" ", "")
    if not phone.startswith("+"):
         await message.answer("❌ Noto'g'ri format. Telefon raqami + bilan boshlanishi kerak.", reply_markup=cancel_keyboard())
         return
         
    msg = await message.answer("🔄 Kod yuborilmoqda, kuting...")
    
    result = await userbot_manager.start_auth(phone)
    
    if result.get("ok"):
        await state.update_data(phone=phone)
        await state.update_data(attempts=0)
        await state.set_state(AuthState.waiting_for_code)
        await msg.edit_text(
            f"✅ {phone} raqamiga kod yuborildi.\n"
            f"📲 KODNI TELEGRAM DASTURIDAN QIDIRING (Telegram rasmiy akkauntidan yozishadi, oddiy SMS kelmasligi mumkin)!\n\n"
            f"⚠️ XAVFSIZLIK UCHUN: Telegram kodingizni bloklab qo'ymasligi uchun "
            f"kodni TERSKARI tartibda kiriting!\n"
            f"Masalan: agar kod 12345 bo'lsa, siz botga 54321 deb yuboring.", 
            reply_markup=cancel_keyboard()
        )
    else:
        error_msg = result.get('error', '')
        if 'PHONE_NUMBER_INVALID' in error_msg:
            friendly_err = "Kiritilgan raqam noto'g'ri yoki mavjud emas."
        elif 'PHONE_NUMBER_BANNED' in error_msg:
            friendly_err = "Bu raqam Telegram tomonidan bloklangan."
        elif 'PHONE_NUMBER_FLOOD' in error_msg:
            friendly_err = "Juda ko'p urinishlar! Iltimos, keyinroq qayta urining."
        else:
            friendly_err = "Raqamni tekshirishda xatolik yuz berdi. Qayta tekshirib ko'ring."
        await msg.edit_text(f"❌ Xatolik yuz berdi: {friendly_err}", reply_markup=cancel_keyboard())
        await state.clear()

@router.message(AuthState.waiting_for_code)
async def process_code(message: Message, state: FSMContext):
    reversed_code = message.text.replace(" ", "").replace("-", "")
    code = reversed_code[::-1]
    
    data = await state.get_data()
    phone = data.get("phone")
    attempts = data.get("attempts", 0)
    
    msg = await message.answer("🔄 Kod tekshirilmoqda...")
    
    result = await userbot_manager.sign_in(phone, code)
    
    if result.get("ok"):
        if result.get("requires_password"):
            await state.set_state(AuthState.waiting_for_password)
            await msg.edit_text("🔐 Ikki bosqichli autentifikatsiya (2FA) parolini kiriting:", reply_markup=cancel_keyboard())
        else:
            await msg.edit_text("✅ Akkaunt muvaffaqiyatli qo'shildi!")
            from handlers.start import get_accounts_keyboard
            import database
            
            user_id = message.from_user.id
            session_string = result.get("session_string")
            
            await database.add_account(user_id, phone)
            await database.update_account_session(user_id, phone, session_string)
            
            accounts = await database.get_accounts(user_id)
            await message.answer("Mavjud akkauntlaringiz:", reply_markup=get_accounts_keyboard(accounts))
            await state.clear()
    else:
        attempts += 1
        await state.update_data(attempts=attempts)
        if attempts >= 3:
            await msg.edit_text("❌ 3 marta noto'g'ri kod kiritildi. Akkaunt qo'shish bekor qilindi.")
            await userbot_manager.disconnect_auth(phone)
            await state.clear()
        else:
            error_msg = result.get('error', '')
            if 'PHONE_CODE_INVALID' in error_msg or 'PHONE_CODE_EMPTY' in error_msg:
                friendly_err = "Siz kiritgan kod noto'g'ri."
            elif 'PHONE_CODE_EXPIRED' in error_msg:
                friendly_err = "Kod muddati tugagan."
            else:
                friendly_err = "Kod noto'g'ri yoki xatolik yuz berdi."
            
            await msg.edit_text(
                f"❌ {friendly_err}\nQolgan urinishlar: {3 - attempts}\nQaytadan kiriting:", 
                reply_markup=cancel_keyboard()
            )

@router.message(AuthState.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text
    data = await state.get_data()
    phone = data.get("phone")
    attempts = data.get("attempts", 0)
    
    msg = await message.answer("🔄 Parol tekshirilmoqda...")
    
    result = await userbot_manager.check_password(phone, password)
    
    if result.get("ok"):
        await msg.edit_text("✅ Akkaunt muvaffaqiyatli qo'shildi!")
        from handlers.start import get_accounts_keyboard
        import database
        
        user_id = message.from_user.id
        session_string = result.get("session_string")
        
        await database.add_account(user_id, phone)
        await database.update_account_session(user_id, phone, session_string)
        
        accounts = await database.get_accounts(user_id)
        await message.answer("Mavjud akkauntlaringiz:", reply_markup=get_accounts_keyboard(accounts))
        await state.clear()
    else:
        attempts += 1
        await state.update_data(attempts=attempts)
        if attempts >= 3:
            await msg.edit_text("❌ 3 marta noto'g'ri parol kiritildi. Akkaunt qo'shish bekor qilindi.")
            await userbot_manager.disconnect_auth(phone)
            await state.clear()
        else:
            await msg.edit_text(
                f"❌ Noto'g'ri parol! Qolgan urinishlar: {3 - attempts}\nQaytadan kiriting:", 
                reply_markup=cancel_keyboard()
            )
