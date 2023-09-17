from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import MenuCallback


def search_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Search",
            callback_data=MenuCallback(
                name="start-searching",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Extend",
            callback_data=MenuCallback(
                name="extend-search-queries",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Clean",
            callback_data=MenuCallback(
                name="clean-search-queries",
            ).pack(),
        ),
    )
    builder.adjust(2, 2)
    return builder
