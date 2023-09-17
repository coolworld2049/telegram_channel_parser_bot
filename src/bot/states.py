from aiogram.fsm.state import StatesGroup, State


class UserbotAuthState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_confirmation_code = State()


class SearchState(StatesGroup):
    limit = State()
    delay = State()
    level1 = State()
    level2 = State()
    level3 = State()
