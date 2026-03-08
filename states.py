from aiogram.fsm.state import State, StatesGroup

class AuthState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_code = State()
    waiting_for_password = State()

class DownloadState(StatesGroup):
    waiting_for_link = State()
    waiting_for_account = State()
