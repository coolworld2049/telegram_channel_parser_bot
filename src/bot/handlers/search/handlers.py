import json
from contextlib import suppress

import aiohttp
from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, InputMediaDocument, User
from loguru import logger

from bot.callbacks import MenuCallback
from bot.keyboards.search import search_keyboard_builder
from bot.loader import bot
from bot.states import SearchState
from core.settings import get_settings

router = Router(name=__file__)


async def start_search_handler(user: User, state: FSMContext, message_id: int = None):
    with suppress(TelegramBadRequest, TypeError):
        for i in range(message_id - 2, message_id):
            await bot.delete_message(user.id, i)
    state_data = await state.get_data()
    search_queries = state_data.get("search_queries") or []
    search_queries_str = [", ".join(x) for i, x in enumerate(search_queries)]
    search_queries_text = str()
    for i, x in enumerate(search_queries):
        search_queries_text += f"<code>{i}</code>  -  <code>{','.join(x)}</code>\n"
    await state.update_data(search_queries=search_queries)
    await bot.send_message(
        user.id,
        f"<b>Search Menu</b>\n\n{search_queries_text}",
        reply_markup=search_keyboard_builder().as_markup(),
    )


@router.message(Command("search"))
async def start_search_message(message: types.Message, state: FSMContext):
    await message.delete()
    await start_search_handler(message.from_user, state, message.message_id)


@router.callback_query(MenuCallback.filter(F.name == "start-searching"))
async def start_searching(
    query: types.CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    state_data = await state.get_data()
    await search_handler(query.from_user, state_data.get("search_queries"))


@router.callback_query(MenuCallback.filter(F.name == "extend-search-queries"))
async def extend_search_queries(
    query: types.CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    await query.answer("Enter a list of keywords separated by `,`")
    await state.set_state(SearchState.extend)


@router.message(SearchState.extend)
async def extend_search_queries_state(message: types.Message, state: FSMContext):
    with suppress(TelegramBadRequest):
        await bot.delete_message(message.from_user.id, message.message_id - 1)
    state_data = await state.get_data()
    search_queries: list[list] = state_data.get("search_queries")
    new_search_queries = [s.strip() for s in message.text.split(",")]
    search_queries.append(new_search_queries)
    await state.update_data(search_queries=search_queries)
    await start_search_handler(message.from_user, state, message.message_id)


@router.callback_query(MenuCallback.filter(F.name == "delete-search-query"))
async def delete_search_query(
    query: types.CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    state_data = await state.get_data()
    search_queries: list[list] = state_data.get("search_queries")
    if len(search_queries) > 1:
        await query.answer("Enter index of the list of keywords to delete")
        await state.set_state(SearchState.delete)
    else:
        await query.answer("The list of keywords is empty!")


@router.message(SearchState.delete)
async def delete_search_query_state(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    search_queries: list[list] = state_data.get("search_queries")
    index = None
    try:
        index = int(message.text)
        search_queries.pop(index)
        await state.update_data(search_queries=search_queries)
    except Exception as e:
        await message.answer(f"Exception: {e}")


@router.callback_query(MenuCallback.filter(F.name == "replace-search-query"))
async def replace_search_query(
    query: types.CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    state_data = await state.get_data()
    search_queries: list[list] = state_data.get("search_queries")
    if len(search_queries) > 1:
        await query.answer(
            "Enter a list of keywords separated by `,` to replace. Example: 0 - a,b,c"
        )
        await state.set_state(SearchState.replace)
    else:
        await query.answer("The list of keywords is empty!")


@router.message(SearchState.replace)
async def replace_search_query_state(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    search_queries: list[list] = state_data.get("search_queries")
    index = None
    try:
        index = int(message.text.split("-")[0].strip())
        new_search_queries = [s.strip() for s in message.text.split("-")[1].split(",")]
        search_queries[index] = new_search_queries
        await state.update_data(search_queries=search_queries)
    except Exception as e:
        await message.answer(f"Exception: {e}")
    await start_search_handler(message.from_user, state, message.message_id)


@router.callback_query(MenuCallback.filter(F.name == "clean-search-queries"))
async def clean_search_queries(
    query: types.CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    await query.message.delete()
    await state.clear()
    await start_search_handler(query.from_user, state)


async def search_handler(user: types.User, search_queries: list[list]):
    print()
    payload: dict[str, list] = {}
    for i in range(3):
        payload.setdefault(f"level{i + 1}", [""])
    for i, x in enumerate(search_queries):
        i += 1
        if i == 4:
            p = payload.get(f"level{i - 1}")
            p.append({f"level{i - 1}": x})
            payload.update({f"level{i - 1}": p})
        else:
            payload.update({f"level{i}": x})
    caption = (
        f"\n\n<code>{' | '.join(list(map(lambda x: x[0], payload.values())))}</code>"
    )
    await bot.send_message(user.id, "Wait. It will take some time")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{get_settings().USERBOT_API_BASE_URL}/telegram/telethon_search",
            json=payload,
        ) as response:
            data = await response.json()
            if response.status != 200:
                logger.error(data)
                await bot.send_message(user.id, str(data))
            unique_usernames = set(map(lambda it: it["username"], data))
            links = set(map(lambda c: f"https://t.me/{c}", unique_usernames))
            input_query_json = BufferedInputFile(
                json.dumps(payload, indent=2, ensure_ascii=True).encode("utf-8"),
                "input.json",
            )
            result_json = BufferedInputFile(
                json.dumps(data, indent=2, ensure_ascii=True).encode("utf-8"),
                "output.json",
            )
            result_txt = BufferedInputFile(
                "\n".join(links).encode("utf-8"), "links.txt"
            )
            await bot.send_media_group(
                user.id,
                media=[
                    InputMediaDocument(media=result_json),
                    InputMediaDocument(media=result_txt, caption=caption),
                ],
            )
