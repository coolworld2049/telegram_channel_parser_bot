import asyncio
import json
import random
from typing import Any

import aiohttp
from aiogram import types
from bs4 import BeautifulSoup, SoupStrainer
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium_recaptcha_solver import RecaptchaSolver
from tqdm.contrib.telegram import tqdm

from bot.cse.parser import search_channels_lyzem, extract_html
from bot.loader import chrome_options, bot
from bot.search_query_builder.main import generate_search_queries
from core.settings import get_settings


def get_search_queries(queries: list[list]):
    new_search_queries = set()
    for query in generate_search_queries(*queries):
        md = query.model_dump(exclude_none=True).values()
        if len(md) > 0:
            q = " ".join(md).strip(" ")
            new_search_queries.add(q)
    return list(new_search_queries)


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


# async def check_channel_existence(index, channels: list[str]):
#     if not userbot.is_connected:
#         logger.warning({index: f"userbot.is_connected: {userbot.is_connected}"})
#         return channels
#     filtered = []
#     _channels = list(map(lambda x: x.split("/")[-1], channels))
#     step = 200
#     for ch in range(0, len(channels), step):
#         try:
#             if ch == 0:
#                 u = await userbot.get_users(user_ids=_channels[ch:step])
#                 filtered.extend(u)
#             elif ch >= step:
#                 u = await userbot.get_users(user_ids=_channels[ch : step * 2])
#                 filtered.extend(u)
#             elif len(channels) - step == 0:
#                 break
#         except Exception as e:
#             logger.error(e)
#             continue
#     filtered = list(map(lambda x: x.username, filtered))
#     logger.info({index: {"channels": len(channels), "real_channels": len(filtered)}})
#     if len(filtered) < 1:
#         return _channels
#     return filtered


async def check_channel_existence(user, driver: WebDriver, channels: list):
    filtered = []
    try:
        m = "Checking the existence of channels..."
        logger.info(m)
        await bot.send_message(user.id, m)
        for i, channel in enumerate(
            tqdm(  # noqa
                channels,
                total=len(channels),
                token=get_settings().BOT_TOKEN,
                chat_id=user.id,
            )
        ):
            html = extract_html(driver, url=channel)
            link = BeautifulSoup(
                html,
                "lxml",
                parse_only=SoupStrainer(
                    "a", attrs={"class", "tgme_action_button_new shine"}
                ),
            )
            if link:
                filtered.append(channel)
                logger.info(f"{i}/{len(channels)} - channel {channel} EXIST!")
            else:
                logger.info(f"{i}/{len(channels)} - channel {channel} not found")
        logger.info(
            {
                "channels": {len(channels)},
                "real_channels": len(filtered),
            }
        )
    except Exception as e:
        logger.error(e)
        return channels
    return filtered


def pre_log_search_results(index, query):
    log_data = {index: query}
    logger.info(log_data)


def post_log_search_results(
    index, query, search_results_count, search_results: set[str]
):
    log_data = {
        index: {
            query: [
                {
                    "count": search_results_count,
                    "channels": list(search_results),
                }
            ]
        }
    }
    logger.info(json.dumps(log_data, indent=2, ensure_ascii=False))


async def search_handler(user: types.User, queries: list[list], limit=100):
    filtered_search_results = []
    search_results: dict[str, Any] | list = {}
    search_results.setdefault("telegago", set())
    search_results.setdefault("lyzem", set())
    selenium_clots = await get_slots_with_sessions()
    if len(selenium_clots) > 2:
        await bot.send_message(
            user.id, "Wait for the previous selenium session to complete"
        )
        yield None
    await asyncio.sleep(random.randint(1, 2) / 10)
    _queries = get_search_queries(queries)
    driver = webdriver.Remote(
        command_executor=get_settings().SE_WEBDRIVER_URL + "/wd/hub",
        options=chrome_options,
    )
    solver = RecaptchaSolver(driver=driver)
    try:
        for i, query in tqdm(  # noqa
            enumerate(_queries),
            total=len(_queries),
            token=get_settings().BOT_TOKEN,
            chat_id=user.id,
        ):
            try:
                pre_log_search_results(i, query)
                logger.info("Lyzem...")
                _lyzem_channels = search_channels_lyzem(
                    driver,
                    query,
                    limit,
                )
                lyzem_channels = {f"https://t.me/{x}" for x in _lyzem_channels}
                search_results.update(
                    {"lyzem": search_results.get("lyzem").union(lyzem_channels)}
                )
                search_results_count = sum([len(x) for x in search_results.values()])
                post_log_search_results(i, query, search_results_count, lyzem_channels)

                # logger.info("Telegago...")
                # _telegago_channels = search_channels_telegago(
                #     driver,
                #     solver,
                #     query,
                #     limit,
                # )
                # telegago_channels = {f"https://t.me/{x}" for x in _telegago_channels}
                # search_results.update(
                #     {
                #         "telegago": search_results.get("telegago").union(
                #             telegago_channels
                #         )
                #     }
                # )
                # search_results_count = sum([len(x) for x in search_results.values()])
                # post_log_search_results(
                #     i, query, search_results_count, telegago_channels
                # )
            except Exception as e:
                logger.error(f"{i} - {e}")
        _channels = []
        for ch in list(search_results.values()):
            if len(ch) > 0:
                _channels.extend(list(ch))
        search_results = _channels
        yield search_results
        filtered_search_results: list = await check_channel_existence(
            user, driver, search_results
        )
    except SystemExit:
        logger.info("driver quit")
        driver.quit()
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        logger.info(search_results)
        logger.info("Driver quit")
        driver.quit()
    yield filtered_search_results
