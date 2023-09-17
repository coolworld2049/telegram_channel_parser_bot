import re

import aiohttp
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states import UserbotAuthState
from core.settings import get_settings

router = Router(name=__file__)


def validate_phone_number(phone_number, phone_number_pattern=r"^\+?\d{10,15}$"):
    cleaned_phone_number = re.sub(r"\D", "", phone_number)
    if not re.match(phone_number_pattern, cleaned_phone_number):
        return False
    return True


@router.message(Command("auth"))
async def on_start_auth(message: types.Message, state: FSMContext):
    await message.answer("Enter telegram account phone number. Example `+1234567890`:")
    await state.set_state(UserbotAuthState.waiting_for_phone)


@router.message(UserbotAuthState.waiting_for_phone)
async def process_phone_number(message: types.Message, state: FSMContext):
    phone_number = message.text
    if validate_phone_number(phone_number):
        await state.update_data(phone_number=phone_number)
        payload = {"phone": phone_number}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{get_settings().USERBOT_API_BASE_URL}/telegram/auth", json=payload
            ) as response:
                data = await response.json()
            if response.status == 200:
                await message.answer(f"Confirmation code sent")
            else:
                await message.answer(str(data))
        await state.set_state(UserbotAuthState.waiting_for_confirmation_code)
    else:
        await message.answer("Invalid phone number. Please enter a valid phone number:")


@router.message(UserbotAuthState.waiting_for_confirmation_code)
async def process_confirmation_code(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    confirmation_code = message.text
    payload = {"phone": state_data.get("phone_number"), "code": confirmation_code}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{get_settings().USERBOT_API_BASE_URL}/telegram/auth/sign_in",
            json=payload,
        ) as response:
            data = await response.json()
        if response.status == 200:
            await message.answer("Authentication successful! You are now logged in.")
        else:
            await message.answer(
                f"{data}\nInvalid confirmation code. Please enter a valid code:"
            )
            await state.set_state(UserbotAuthState.waiting_for_confirmation_code)
