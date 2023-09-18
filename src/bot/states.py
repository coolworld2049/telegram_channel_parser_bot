from aiogram.fsm.state import StatesGroup, State


class SearchState(StatesGroup):
    extend = State()
    delete = State()
    replace = State()
    change_limit = State()


class SessionState(StatesGroup):
    set = State()
    enter_code = State()
