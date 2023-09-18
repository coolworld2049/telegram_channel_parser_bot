from aiogram.fsm.state import StatesGroup, State


class SearchState(StatesGroup):
    extend = State()
    delete = State()
    replace = State()
    change_limit = State()
