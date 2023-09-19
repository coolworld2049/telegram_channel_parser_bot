from contextlib import suppress

from aiogram import Router, F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import User, Message, CallbackQuery, ErrorEvent
from loguru import logger

from bot.callbacks import MenuCallback
from bot.handlers import search
from bot.loader import bot
from bot.template_engine import render_template

router = Router(name=__file__)
router.include_routers(*[search.router])


@router.error(
    ExceptionTypeFilter(TelegramBadRequest),
    F.update.callback.as_("query"),
)
async def handle_my_custom_exception(event: ErrorEvent, query: types.CallbackQuery):
    logger.error(event.exception.args)


async def start_handler(user: User, state: FSMContext, message_id: int):
    await state.clear()
    await bot.send_message(
        user.id,
        render_template(
            "start.html",
            user=user,
            bot=await bot.me(),
        ),
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
