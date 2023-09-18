import json
import pathlib

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import bot.userbot
from bot.handlers.search.handlers import start_search_handler
from bot.loader import bot
from bot.userbot import userbot
from bot.states import SessionState
from core.settings import get_settings

router = Router(name=__file__)

destination = pathlib.Path(__file__).parent.parent.parent


async def start_userbot_client(account: dict):
    p = destination.joinpath("pyrogram_account.json")
    p.open("w").write(json.dumps(account, indent=2))

    session_string_p = destination.joinpath("pyrogram.txt")
    if session_string_p.exists():
        bot.userbot.session_string = session_string_p.open("r").read().strip()
        userbot.in_memory = True
    else:
        userbot.api_id = account.get("api_id")
        userbot.api_hash = account.get("api_hash")
        userbot.phone_number = account.get("phone_number")
    await userbot.start()
    session = await userbot.export_session_string()
    session_string_p.open("w").write(session)


@router.message(Command("start_userbot"))
async def start_userbot(message: types.Message, state: FSMContext):
    if (
        message.from_user.id not in get_settings().BOT_ACL
        and get_settings().BOT_ACL_ENABLED
    ):
        return None
    try:
        account: dict = json.loads(
            destination.joinpath("pyrogram_account.json").open("r").read()
        )
        await start_userbot_client(account)
        await start_search_handler(message.from_user, state, message.message_id)
    except Exception as e:
        await message.answer(str(e))


@router.message(Command("set_session"))
async def set_session(message: types.Message, state: FSMContext):
    if (
        message.from_user.id not in get_settings().BOT_ACL
        and get_settings().BOT_ACL_ENABLED
    ):
        return None
    await state.clear()
    await message.answer(
        "Send file pyrogram.session with caption api_key, api_hash, phone_number.\n"
        "Example <code>1234:qwerty:7111111111</code>"
    )
    await state.set_state(SessionState.upload_session)


@router.message(SessionState.upload_session, F.document)
async def upload_session_state(message: types.Message, state: FSMContext):
    data = message.caption.split(":")
    if len(data) != 3:
        await message.answer("Invalid input")
        return None
    account = {
        "api_id": data[0],
        "api_hash": data[1],
        "phone_number": data[2],
    }
    try:
        await start_userbot_client(account)
        await bot.download(
            message.document.file_id,
            destination=destination / "pyrogram.session",
        )
        await state.clear()
        await start_search_handler(message.from_user, state, message.message_id)
    except Exception as e:
        await message.answer(str(e))
