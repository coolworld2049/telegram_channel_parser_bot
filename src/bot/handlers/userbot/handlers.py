import json
import pathlib

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.handlers.search.handlers import start_search_handler
from bot.states import SessionState
from bot.userbot import userbot
from core.settings import get_settings

router = Router(name=__file__)

destination = pathlib.Path(__file__).parent.parent.parent


@router.message(Command("authorize"))
async def set_session(message: types.Message, state: FSMContext):
    if (
        message.from_user.id not in get_settings().BOT_ACL
        and get_settings().BOT_ACL_ENABLED
    ):
        return None
    await state.clear()
    await message.answer(
        "Enter api_key, api_hash, phone_number.\n"
        "Example <code>1234:qwerty:7111111111</code>"
    )
    await state.set_state(SessionState.send_code)


@router.message(SessionState.send_code)
async def upload_session_state(message: types.Message, state: FSMContext):
    data = message.caption.split(":")
    if len(data) != 3:
        await message.answer("Invalid input")
        return None
    try:
        account = {
            "api_id": int(data[0]),
            "api_hash": data[1],
            "phone_number": data[2],
        }
    except Exception as e:  # noqa
        await message.answer("api_id must be an integer")
        return None
    userbot.api_id = account.get("api_id")
    userbot.api_hash = account.get("api_hash")
    userbot.phone_number = account.get("phone_number")
    await userbot.connect()
    sent_code = await userbot.send_code(account.get("phone_number"))
    await state.update_data(account=account, phone_code_hash=sent_code.phone_code_hash)
    await message.answer("Enter confirmation code: ")
    await state.set_state(SessionState.sign_in)


@router.message(SessionState.sign_in)
async def sign_in_state(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    account = state_data.get("account")
    phone_code_hash = state_data.get("phone_code_hash")
    try:
        await userbot.connect()
        await userbot.sign_in(
            account.get("phone_number"), phone_code_hash, message.text
        )
        session = await userbot.export_session_string()
        destination.joinpath("pyrogram.txt").open("w").write(str(session))
        destination.joinpath("pyrogram_account.json").open("w").write(
            json.dumps(account, indent=2)
        )
    except Exception as e:
        await message.answer(str(e))
    await state.clear()
    await start_search_handler(message.from_user, state, message.message_id)
