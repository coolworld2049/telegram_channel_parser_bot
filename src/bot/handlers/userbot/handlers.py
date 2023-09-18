import pathlib

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.handlers.search.handlers import start_search_handler
from bot.loader import bot, userbot
from bot.states import SessionState
from core.settings import get_settings

router = Router(name=__file__)

destination = pathlib.Path(__file__).parent.parent.parent


@router.message(Command("set_session"))
async def set_session(message: types.Message, state: FSMContext):
    if (
        message.from_user.id not in get_settings().BOT_ACL
        and get_settings().BOT_ACL_ENABLED
    ):
        return None
    await state.clear()
    await message.answer("Send pyrogram.session file")
    await state.set_state(SessionState.set)


@router.message(SessionState.set, F.document)
async def set_session_state(message: types.Message, state: FSMContext):
    await bot.download(
        message.document.file_id,
        destination=destination / "pyrogram.session",
    )
    try:
        await userbot.start()
        await message.answer("Enter confirmation code:")
    except Exception as e:
        await message.answer(str(e))


@router.message(SessionState.enter_code)
async def enter_code_state(message: types.Message, state: FSMContext):
    try:
        session = await userbot.export_session_string()
        destination.joinpath("pyrogram.txt").open("w").write(session)
        bot.userbot = userbot
        await state.clear()
    except Exception as e:
        await message.answer(str(e))
    await start_search_handler(message.from_user, state, message.from_user.message_id)
