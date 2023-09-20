import aiohttp
from aiogram import types
from bs4 import BeautifulSoup
from loguru import logger
from tqdm.contrib.telegram import tqdm

from bot.cse.parser import search_channels_lyzem
from bot.loader import bot, selenium_webdriver
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
            try:
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
            except Exception as e:
                logger.info({"index": i, "exception": e})
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
            channel_exist = await check_channel_existence(channel)
            if channel_exist and channel:
                filtered_search_results.append(channel)
                logger.info(f"{i}/{len(search_results)} channel {channel} EXIST!")
            else:
                logger.info(f"{i}/{len(search_results)} channel {channel} not found")
    except Exception as e:
        logger.error(e)
    finally:
        return set(filtered_search_results)


async def check_channel_existence(url):
    url = url.replace("t.me/", "t.me/s/")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "lxml")
                link = soup.find("a", class_="tgme_header_link")
                if link:
                    return True
                return False
    except aiohttp.ClientError as e:
        logger.error(f"An error occurred: {e}")
        return False
