import json

import aiohttp
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from loguru import logger

from bot.states import SearchState
from core.settings import get_settings

router = Router(name=__file__)


@router.message(Command("search"))
async def start_search(message: types.Message, state: FSMContext):
    await message.reply("Enter the 1 level keywords:")
    await state.set_state(SearchState.level1)


@router.message(SearchState.level1)
async def process_level1(message: types.Message, state: FSMContext):
    level1 = [s.strip() for s in message.text.split(",")]
    await state.update_data(level1=level1)
    await message.reply("Enter the 2 level keywords:")
    await state.set_state(SearchState.level2)


@router.message(SearchState.level2)
async def process_level2(message: types.Message, state: FSMContext):
    level2 = [s.strip() for s in message.text.split(",")]
    await state.update_data(level2=level2)
    await message.reply("Enter the 3 level keywords:")
    await state.set_state(SearchState.level3)


@router.message(SearchState.level3)
async def process_level3(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    level3 = [s.strip() for s in message.text.split(",")]
    payload = {
        "level1": state_data.get("level1"),
        "level2": state_data.get("level2"),
        "level3": level3,
    }
    caption = f"\n\n<code>{json.dumps(payload, indent=2)}</code>"
    await state.clear()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{get_settings().USERBOT_API_BASE_URL}/telegram/search",
            json=payload,
        ) as response:
            data = await response.json()
            if response.status != 200:
                logger.error(data)
                await message.answer(data)
            await message.reply_document(
                document=BufferedInputFile(
                    json.dumps(data, indent=2).encode("utf-8"), "result.json"
                ),
                caption=caption,
            )
