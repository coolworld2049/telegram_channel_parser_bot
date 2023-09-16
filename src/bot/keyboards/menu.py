from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks import MenuCallback


def menu_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Button",
            callback_data=MenuCallback(
                name="button",
            ).pack(),
        ),
    )
    builder.adjust(2, 2)
    return builder
