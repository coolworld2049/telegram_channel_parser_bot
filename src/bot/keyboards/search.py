from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import MenuCallback


def search_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔍",
            callback_data=MenuCallback(
                name="start-searching",
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Set limit per query",
            callback_data=MenuCallback(
                name="change-search-limit",
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Set min subscribers",
            callback_data=MenuCallback(
                name="change-min-subscribers",
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="➕",
            callback_data=MenuCallback(
                name="extend-search-queries",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="➖",
            callback_data=MenuCallback(
                name="delete-search-query",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="🔄",
            callback_data=MenuCallback(
                name="replace-search-query",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="🗑️",
            callback_data=MenuCallback(
                name="clean-search-queries",
            ).pack(),
        ),
    )
    return builder
