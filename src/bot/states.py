from aiogram.fsm.state import StatesGroup, State


class SearchState(StatesGroup):
    extend = State()
    delete = State()
    replace = State()
    change_limit = State()


class SessionState(StatesGroup):
    set_creds = State()
    send_code = State()
    sign_in = State()
