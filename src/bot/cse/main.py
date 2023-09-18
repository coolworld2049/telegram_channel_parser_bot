import asyncio
import json
import random

import aiohttp
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from loguru import logger
from selenium import webdriver
from selenium_recaptcha_solver import RecaptchaSolver
from tqdm.contrib.telegram import trange

from bot.cse.parser import search_channels_lyzem
from bot.loader import chrome_options, user_agent, bot
from bot.search_query_builder.main import generate_search_queries
from core.settings import get_settings


def get_search_queries(queries: list[list]):
    new_search_queries = set()
    for query in generate_search_queries(*queries):
        md = query.model_dump(exclude_none=True).values()
        if len(md) > 0:
            q = " ".join(md).strip(" ")
            new_search_queries.add(q)
    new_search_queries = sorted(new_search_queries, key=lambda x: len(x))
    return new_search_queries


async def get_slots_with_sessions():
    async with aiohttp.ClientSession() as session:
        async with session.get(get_settings().SE_WEBDRIVER_URL + "/status") as response:
            if response.status == 200:
                data = await response.text()
                json_data = json.loads(data)
                slots_with_sessions = []
                for node in json_data["value"]["nodes"]:
                    for slot in node["slots"]:
                        if slot["session"] is not None:
                            slots_with_sessions.append(slot)

                return slots_with_sessions
            else:
                print(f"Failed to retrieve data. Status code: {response.status}")
                return []


async def search_handler(user: types.User, queries: list[list], limit=100):
    if len(await get_slots_with_sessions()) > 2:
        await bot.send_message(user.id, "Wait for previous requests to complete")
        return None
    await asyncio.sleep(random.randint(1, 2) / 10)
    search_results = {}
    search_results.setdefault("telegago", set())
    search_results.setdefault("lyzem", set())
    _queries = get_search_queries(queries)
    chrome_options.add_argument(f"--user-agent={user_agent.random}")
    driver = webdriver.Remote(
        command_executor=get_settings().SE_WEBDRIVER_URL + "/wd/hub",
        options=chrome_options,
    )
    solver = RecaptchaSolver(driver=driver)
    try:
        for q in trange(  # noqa
            len(_queries),
            total=len(_queries),
            token=get_settings().BOT_TOKEN,
            chat_id=user.id,
        ):
            _q = _queries[q]
            try:
                lyzem_channels = search_channels_lyzem(driver, solver, _q, limit=limit)
                search_results.update(
                    {
                        "lyzem": search_results.get("lyzem").union(
                            {f"https://t.me/{x}" for x in lyzem_channels}
                        )
                    }
                )
                # telegago_channels = search_channels_telegago(
                #     driver, solver, _q, limit=limit
                # )
                # search_results.update(
                #     {
                #         "telegago": search_results.get("telegago").union(
                #             {f"https://t.me/{x}" for x in telegago_channels}
                #         )
                #     }
                # )
            except Exception as e:
                logger.error(e)
            logger.debug(
                f"{_q}; lyzem_channels: {len(search_results.get('lyzem'))},"
                f" telegago_channels: {len(search_results.get('telegago'))}"
            )
    except Exception as e:
        logger.error(e)
        raise e
    except TelegramBadRequest:
        pass
    finally:
        driver.quit()
    return search_results
