from aiogram.fsm.state import StatesGroup, State


class UserbotAuthState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_confirmation_code = State()
