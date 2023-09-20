import asyncio
import random

import aiohttp
from aiogram import types
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium_recaptcha_solver import RecaptchaSolver
from tqdm.contrib.telegram import tqdm

from bot.cse.parser import (
    search_channels_lyzem,
    search_channels_telegago,
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


async def telegram_parsing_handler(user: types.User, queries: list[str], limit=100):
    search_results = []
    filtered_search_results = []

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
        for i, query in tqdm(  # noqa
            enumerate(queries),
            total=len(queries),
            token=get_settings().BOT_TOKEN,
            chat_id=user.id,
        ):
            lyzem_channels = search_channels_lyzem(
                selenium_webdriver,
                query,
                limit,
            )
            search_results.extend(lyzem_channels)
            logger.info(
                {
                    "index": i,
                    "query": query,
                    "unique_channels": len(set(search_results)),
                }
            )
        search_results = set(search_results)
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
            channel_exist = await check_channel_existence(channel, 3)
            if channel_exist and channel:
                filtered_search_results.append(channel)
                logger.info(f"{i}/{len(search_results)} channel {channel} EXIST!")
            else:
                logger.info(f"{i}/{len(search_results)} channel {channel} not found")
    except Exception as e:
        logger.error(e)
    finally:
        return set(filtered_search_results)


async def check_channel_existence(url, retries):
    url = url.replace("t.me/", "t.me/s/")
    headers = {
        'User-Agent': user_agent.random,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "lxml")
                link = soup.find("a", class_="tgme_header_link")
                if link:
                    return True
                return False
    except aiohttp.ClientError as e:
        logger.error(f"url {url}. An error occurred: {e}")
        if retries <= 0:
            return False
        logger.info("Retry")
        await check_channel_existence(url, retries - 1)


