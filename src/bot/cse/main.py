import asyncio
import random

import aiohttp
from aiogram import types
from aiogram.types import BufferedInputFile
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium_recaptcha_solver import RecaptchaSolver
from tqdm.contrib.telegram import tqdm

from bot.cse.parser import (
    search_channels_lyzem,
)
from bot.loader import bot, user_agent, chrome_options
from bot.settings import get_settings


async def selenium_remote_sessions(path="status"):
    url = get_settings().SE_WEBDRIVER_URL + f"/{path}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    json_data = await response.json()
                    slots_with_sessions = []

                    for node in json_data["value"]["nodes"]:
                        for slot in node["slots"]:
                            if slot["session"] is not None:
                                slots_with_sessions.append(slot)

                    return slots_with_sessions
                else:
                    print(f"Failed to retrieve data. Status code: {response.status}")
                    return []
    except aiohttp.ClientError as e:
        print(f"An error occurred: {e}")
        return []


async def telegram_parsing_handler(
    user: types.User, queries: list[str], limit, min_subscribers
):
    search_results = set()
    filtered_search_results = set()

    selenium_webdriver = webdriver.Remote(
        command_executor=get_settings().SE_WEBDRIVER_URL + "/wd/hub",
        options=chrome_options,
    )
    solver = RecaptchaSolver(selenium_webdriver)
    selenium_slots = await selenium_remote_sessions()
    if len(selenium_slots) > 2:
        await bot.send_message(
            user.id, "Wait for the previous selenium session to complete"
        )
    try:
        max_page_number = 1 if limit <= 100 else 2
        for i, query in tqdm(  # noqa
            enumerate(queries),
            total=len(queries),
            token=get_settings().BOT_TOKEN,
            chat_id=user.id,
        ):
            lyzem_channels = search_channels_lyzem(
                selenium_webdriver, query, limit, max_page_number=max_page_number
            )
            for lch in lyzem_channels:
                search_results.add(lch)
            logger.info(
                {
                    "index": i,
                    "query": query,
                    "channels": len(lyzem_channels),
                    "all_channels": len(search_results),
                }
            )
        output = BufferedInputFile(
            "\n".join(list(search_results)).encode("utf-8"), "result.txt"
        )
        if output.data != b"":
            await bot.send_document(user.id, output)
        m = "Check for channels existence"
        logger.info(m)
        await bot.send_message(user.id, "Check for channels existence")
        for i, channel in tqdm(  # noqa
            enumerate(search_results),
            total=len(search_results),
            token=get_settings().BOT_TOKEN,
            chat_id=user.id,
        ):
            await asyncio.sleep(random.randint(1, 2) / 10)
            channel_exist = await check_channel_existence(
                channel, 3, min_subscribers=min_subscribers
            )
            if channel_exist:
                filtered_search_results.add(channel)
                logger.info(f"{i}/{len(search_results)} channel {channel} ADDED")
            else:
                logger.info(f"{i}/{len(search_results)} channel {channel} EXCLUDED")
            logger.info(
                f"unique_filtered_search_results: {len(filtered_search_results)}"
            )
    except Exception as e:
        logger.error(e)
    finally:
        return filtered_search_results


async def check_channel_existence(url, retries=3, *, min_subscribers):
    headers = {
        "User-Agent": user_agent.random,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "lxml")
                tgme_page_extra = soup.find("div", attrs="tgme_page_extra")
                if (
                    tgme_page_extra
                    and "no members" not in tgme_page_extra.text
                    and "@" not in tgme_page_extra.text
                    and "no subscribers" not in tgme_page_extra
                ):
                    subscribers_counter_str = tgme_page_extra.text.split(" ")[0]
                    subscribers_counter = 0
                    if "K" not in subscribers_counter_str:
                        subscribers_counter = int(subscribers_counter_str)
                    else:
                        number = subscribers_counter_str.split("K")[0]
                        subscribers_counter = int(float(number) * 1000)
                    logger.info(
                        f"url {url} subscribers_counter_str: {subscribers_counter_str}; subscribers_counter: {subscribers_counter}; min_subscribers: {min_subscribers}"
                    )
                    if subscribers_counter >= min_subscribers:
                        return True
                    else:
                        return False
                else:
                    return False
    except Exception as e:
        logger.error(f"url {url}. An error occurred: {e}")
        if retries <= 0:
            return False
        logger.info(f"url {url}. Retry")
        await check_channel_existence(url, retries - 1, min_subscribers=min_subscribers)
