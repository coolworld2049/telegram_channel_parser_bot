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
    builder.row(
        InlineKeyboardButton(
            text="Set limit",
            callback_data=MenuCallback(
                name="change-search-limit",
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Add",
            callback_data=MenuCallback(
                name="extend-search-queries",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Update",
            callback_data=MenuCallback(
                name="replace-search-query",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Delete",
            callback_data=MenuCallback(
                name="delete-search-query",
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Clean",
            callback_data=MenuCallback(
                name="clean-search-queries",
            ).pack(),
        ),
    )
    return builder
