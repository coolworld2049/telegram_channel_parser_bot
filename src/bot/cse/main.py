import requests
from aiogram import types
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from tqdm.contrib.telegram import tqdm

from bot.cse.parser import search_channels_lyzem, extract_html
from bot.loader import chrome_options, bot
from bot.settings import get_settings


def selenium_remote_sessions(path="status"):
    url = get_settings().SE_WEBDRIVER_URL + f"/{path}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        slots_with_sessions = []
        for node in json_data["value"]["nodes"]:
            for slot in node["slots"]:
                if slot["session"] is not None:
                    slots_with_sessions.append(slot)

        return slots_with_sessions
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return []


async def telegram_parsing_handler(user: types.User, queries: list[str], limit=100):
    search_results = []
    filtered_search_results = []
    selenium_slots = selenium_remote_sessions()
    if len(selenium_slots) > 2:
        await bot.send_message(
            user.id, "Wait for the previous selenium session to complete"
        )
    selenium_webdriver = webdriver.Remote(
        command_executor=get_settings().SE_WEBDRIVER_URL + "/wd/hub",
        options=chrome_options,
    )
    try:
        for i, query in tqdm(  # noqa
            enumerate(queries),
            total=len(queries),
            token=get_settings().BOT_TOKEN,
            chat_id=user.id,
        ):
            try:
                logger.info({"index": i, "query": query})
                lyzem_channels = search_channels_lyzem(
                    selenium_webdriver,
                    query,
                    limit,
                )
                search_results.extend(lyzem_channels)
                logger.info(
                    {"index": i, "query": query, "channels": len(lyzem_channels)}
                )
            except Exception as e:
                logger.info({"index": i, "exception": e})
        yield set(search_results)
        m = "Check for channels existence"

        await bot.send_message(user.id, "Check for channels existence")
        for i, channel in tqdm(  # noqa
            enumerate(search_results),
            total=len(search_results),
            token=get_settings().BOT_TOKEN,
            chat_id=user.id,
        ):
            channel_exist = check_channel_existence(selenium_webdriver, channel)
            if channel_exist:
                filtered_search_results.append(channel)
                logger.info(f"{i}/{len(search_results)} channel {channel} EXIST!")
            else:
                logger.debug(f"{i}/{len(search_results)} channel {channel} not found")
    except Exception as e:
        logger.error(e)
    finally:
        logger.info("Selenium webdriver: quit and stop client")
        selenium_webdriver.quit()
        selenium_webdriver.stop_client()
    yield set(filtered_search_results)


def check_channel_existence(driver, url):
    url = url.replace("t.me/", "t.me/s/")
    tme_html = extract_html(driver, url=url, timeout=False)
    soup = BeautifulSoup(tme_html, "lxml")
    link = soup.find("a", attrs={"class", "tgme_header_link"})
    logger.debug({"url": url, "link": link})
    if link:
        return True
    return False
