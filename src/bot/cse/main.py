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

from bot.cse.parser import search_channels_lyzem, search_channels_telegago
from bot.loader import chrome_options, user_agent, bot, userbot
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


async def check_channel_existence(index, channels: list[str]):
    if not userbot.is_connected:
        logger.warning({index: f"userbot.is_connected: {userbot.is_connected}"})
        return channels
    filtered = []
    _channels = list(map(lambda x: x.split("/")[-1], channels))
    step = 200
    for ch in range(0, len(channels), step):
        try:
            if ch == 0:
                u = await userbot.get_users(user_ids=_channels[ch:step])
                filtered.extend(u)
            elif ch >= step:
                u = await userbot.get_users(user_ids=_channels[ch : step * 2])
                filtered.extend(u)
            elif len(channels) - step == 0:
                break
        except Exception as e:
            logger.error(e)
            continue
    filtered = list(map(lambda x: x.username, filtered))
    logger.info({index: {"channels": len(channels), "real_channels": len(filtered)}})
    if len(filtered) < 1:
        return _channels
    return filtered


def pre_log_search_results(index, query):
    log_data = {index: query}
    logger.info(log_data)


def post_log_search_results(
    index, query, search_results_count, search_results: list[str]
):
    log_data = {
        index: {
            query: [
                {
                    "count": search_results_count,
                    "channels": search_results,
                }
            ]
        }
    }
    logger.info(json.dumps(log_data, indent=2, ensure_ascii=False))


async def search_handler(user: types.User, queries: list[list], limit=100):
    search_results = {}
    search_results.setdefault("telegago", set())
    search_results.setdefault("lyzem", set())
    selenium_clots = await get_slots_with_sessions()
    if len(selenium_clots) > 2:
        await bot.send_message(
            user.id, "Wait for the previous selenium session to complete"
        )
        return search_results
    await asyncio.sleep(random.randint(1, 2) / 10)
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
                pre_log_search_results(q, _q)
                logger.info("Lyzem...")
                _lyzem_channels = search_channels_lyzem(
                    driver,
                    solver,
                    _q,
                    limit,
                )
                _lyzem_channels = {f"https://t.me/{x}" for x in _lyzem_channels}
                lyzem_channels = await check_channel_existence(q, list(_lyzem_channels))
                search_results.update(
                    {"lyzem": search_results.get("lyzem").union(lyzem_channels)}
                )
                search_results_count = sum([len(x) for x in search_results.values()])
                post_log_search_results(q, _q, search_results_count, lyzem_channels)

                logger.info("Telegago...")
                _telegago_channels = search_channels_telegago(
                    driver,
                    solver,
                    _q,
                    limit,
                )
                _telegago_channels = {f"https://t.me/{x}" for x in _telegago_channels}
                telegago_channels = await check_channel_existence(
                    q, list(_telegago_channels)
                )
                search_results.update(
                    {
                        "telegago": search_results.get("telegago").union(
                            telegago_channels
                        )
                    }
                )
                search_results_count = sum([len(x) for x in search_results.values()])
                post_log_search_results(q, _q, search_results_count, telegago_channels)
            except Exception as e:
                logger.error(f"{q} - {e}")
    except Exception as e:
        logger.error(e)
        raise e
    except TelegramBadRequest:
        pass
    finally:
        logger.info(search_results)
        logger.info("End")
        driver.quit()
    return search_results
