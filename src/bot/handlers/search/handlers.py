from contextlib import suppress

from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, InputMediaDocument, User

from bot.callbacks import MenuCallback
from bot.cse.main import telegram_parsing_handler
from bot.cse.query_builder import get_generated_search_queries
from bot.keyboards.search import search_keyboard_builder
from bot.loader import bot
from bot.states import SearchState
from bot.template_engine import render_template
from bot.settings import get_settings

router = Router(name=__file__)


async def start_search_handler(user: User, state: FSMContext, message_id: int = None):
    with suppress(TelegramBadRequest, TypeError):
        await bot.delete_message(user.id, message_id - 1)
    state_data = await state.get_data()
    search_queries = state_data.get("search_queries") or []
    limit_per_query = state_data.get("limit") or 100
    keywords = [", ".join(x) for i, x in enumerate(search_queries)]
    generated_search_queries = list(get_generated_search_queries(search_queries))
    await state.update_data(search_queries=search_queries)
    await bot.send_message(
        user.id,
        render_template(
            "search_menu.html",
            query_count=len(generated_search_queries),
            limit_per_query=limit_per_query,
            keywords=enumerate(keywords),
        ),
        reply_markup=search_keyboard_builder().as_markup(),
    )


@router.message(Command("search"))
async def start_search_message(message: types.Message, state: FSMContext):
    if (
        message.from_user.id not in get_settings().BOT_ACL
        and get_settings().BOT_ACL_ENABLED
    ):
        return None
    await start_search_handler(message.from_user, state, message.message_id)


@router.callback_query(MenuCallback.filter(F.name == "start-searching"))
async def start_searching(
    query: types.CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    state_data = await state.get_data()
    search_queries = state_data.get("search_queries")
    if not search_queries:
        await query.answer("There are no keywords list")
        return None
    generated_queries = get_generated_search_queries(search_queries)
    async for channels in telegram_parsing_handler(
        query.from_user, generated_queries, limit=state_data.get("limit") or 100
    ):
        if not channels:
            await bot.send_message(query.from_user.id, "No channels found")
            continue
        search_queries_fragment = " | ".join(list(map(lambda x: x[0], search_queries)))
        caption = render_template(
            "parse_result.html",
            query=search_queries_fragment,
            channels_count=len(channels),
        )
        input = BufferedInputFile(
            "\n".join(list(map(lambda x: ", ".join(x), search_queries))).encode(
                "utf-8"
            ),
            filename="input.txt",
        )
        output = BufferedInputFile("\n".join(channels).encode("utf-8"), "output.txt")
        names = BufferedInputFile(
            "\n".join(map(lambda x: x.split("/")[-1], channels)).encode("utf-8"),
            filename="names.txt",
        )
        await bot.send_media_group(
            query.from_user.id,
            media=[
                InputMediaDocument(media=input),
                InputMediaDocument(media=output),
                InputMediaDocument(media=names, caption=caption),
            ],
        )
        await bot.send_message(query.from_user.id, caption)


@router.callback_query(MenuCallback.filter(F.name == "change-search-limit"))
async def change_search_limit(
    query: types.CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    await query.answer("Enter a limit per query")
    await state.set_state(SearchState.change_limit)


@router.message(SearchState.change_limit)
async def change_search_limit_state(message: types.Message, state: FSMContext):
    try:
        await state.update_data(limit=int(message.text))
    except Exception as e:
        await message.answer("Limit must be an integer")
        await state.clear()
    await start_search_handler(message.from_user, state, message.message_id)


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
    search_queries: list[list] = state_data.get("search_queries") or []
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
        await state.clear()


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
        await state.clear()
    await start_search_handler(message.from_user, state, message.message_id)


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
        await state.clear()
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
        await state.clear()
    await start_search_handler(message.from_user, state, message.message_id)


@router.callback_query(MenuCallback.filter(F.name == "clean-search-queries"))
async def clean_search_queries(
    query: types.CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    await query.message.delete()
    await state.clear()
    await start_search_handler(query.from_user, state)
