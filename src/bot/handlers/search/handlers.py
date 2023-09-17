import json

import aiohttp
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, InputMediaDocument
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
    caption = (
        f"\n\n<code>{' | '.join(list(map(lambda x:x[0], payload.values())))}</code>"
    )
    await state.clear()
    await message.answer("Wait. It will take some time")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{get_settings().USERBOT_API_BASE_URL}/telegram/search",
            json=payload,
        ) as response:
            data = await response.json()
            if response.status != 200:
                logger.error(data)
                await message.answer(data)
            unique_usernames = set(map(lambda it: it["username"], data))
            links = set(map(lambda c: f"https://t.me/{c}", unique_usernames))
            result_json = BufferedInputFile(
                json.dumps(data, indent=2, ensure_ascii=True).encode("utf-8"),
                "result.json",
            )
            result_txt = BufferedInputFile(
                "\n".join(links).encode("utf-8"), "result.txt"
            )
            await message.reply_media_group(
                media=[
                    InputMediaDocument(media=result_json),
                    InputMediaDocument(media=result_txt, caption=caption),
                ],
                caption=caption,
            )
