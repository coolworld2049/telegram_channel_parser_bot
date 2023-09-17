from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import MenuCallback


def search_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Search",
            callback_data=MenuCallback(
                name="start-searching",
            ).pack(),
        ),
    )
    builder.add(
        InlineKeyboardButton(
            text="Extend",
            callback_data=MenuCallback(
                name="extend-search-queries",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Delete by index",
            callback_data=MenuCallback(
                name="delete-search-query",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Replace by index",
            callback_data=MenuCallback(
                name="replace-search-query",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Clean",
            callback_data=MenuCallback(
                name="clean-search-queries",
            ).pack(),
        ),
    )
    builder.adjust(2, 4)
    return builder
