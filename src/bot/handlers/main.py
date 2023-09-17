from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import User, Message, CallbackQuery

from bot.callbacks import MenuCallback
from bot.handlers import search, auth
from bot.keyboards.menu import (
    menu_keyboard_builder,
)
from bot.loader import bot
from bot.template_engine import render_template

router = Router(name=__file__)
router.include_routers(*[search.router, auth.router])


async def start_handler(user: User, state: FSMContext, message_id: int):
    await state.clear()
    await bot.send_message(
        user.id,
        render_template(
            "start.html",
            user=user,
            bot=await bot.me(),
        ),
        # reply_markup=menu_keyboard_builder().as_markup(),
    )


@router.message(Command("start"))
async def start_message(message: Message, state: FSMContext):
    await start_handler(message.from_user, state, message.message_id)


@router.callback_query(MenuCallback.filter(F.name == "start"))
async def start_callback(
    query: CallbackQuery,
    state: FSMContext,
):
    with suppress(TelegramBadRequest):
        await query.message.delete()
    await start_handler(query.from_user, state, query.message.message_id)
