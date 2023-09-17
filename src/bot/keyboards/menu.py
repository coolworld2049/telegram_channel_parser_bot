from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import MenuCallback


def menu_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Search",
            callback_data=MenuCallback(
                name="search",
            ).pack(),
        ),
    )
    builder.adjust(2, 2)
    return builder
