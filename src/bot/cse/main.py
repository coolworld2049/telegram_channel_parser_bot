import asyncio
import random

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_recaptcha_solver import RecaptchaSolver
from tqdm.contrib.telegram import trange
from webdriver_manager.chrome import ChromeDriverManager

from bot.cse.parser import search_channels_lyzem
from bot.search_query_builder.main import generate_search_queries
from core.settings import get_settings


def get_search_queries(queries: list[list]):
    new_search_queries = set()
    for query in generate_search_queries(*queries):
        md = query.model_dump(exclude_none=True).values()
        if len(md) > 0:
            q = " ".join(md).strip(" ")
            new_search_queries.add(q)
    new_search_queries = sorted(new_search_queries, key=lambda x: len(x), reverse=True)
    return new_search_queries


async def search_handler(user: types.User, queries: list[list], limit=100, delay=2):
    await asyncio.sleep(random.randint(1, 2) / 10)
    search_results = {}
    search_results.setdefault("telegago", set())
    search_results.setdefault("lyzem", set())
    _queries = get_search_queries(queries)

    options = Options()
    options.add_argument("--headless")  # Enable headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--remote-allow-origins=*")

    # driver = webdriver.Chrome(
    #     service=Service(ChromeDriverManager().install()), options=chrome_options
    # )
    # ChromeDriverManager().install()

    driver = webdriver.Remote(
        command_executor="http://localhost:4444/wd/hub", options=options
    )

    # driver.implicitly_wait(10)

    solver = RecaptchaSolver(driver=driver)

    try:
        for q in trange(  # noqa
            len(_queries),
            total=len(_queries),
            token=get_settings().BOT_TOKEN,
            chat_id=user.id,
        ):
            _q = _queries[q]
            await asyncio.sleep(random.randint(1, 10 * delay) / 10)
            lyzem_channels = search_channels_lyzem(driver, solver, _q, limit=limit)
            search_results.update(
                {
                    "lyzem": search_results.get("lyzem").union(
                        {f"https://t.me/{x}" for x in lyzem_channels}
                    )
                }
            )
            # await asyncio.sleep(random.randint(1, 10 * delay) / 10)
            # telegago_channels = search_channels_telegago(_q, limit=limit)
            # search_results.update(
            #     {
            #         "telegago": search_results.get("telegago").union(
            #             {f"https://t.me/{x}" for x in telegago_channels}
            #         )
            #     }
            # )
            logger.debug(
                f"{_q}; lyzem_channels: {len(search_results.get('lyzem'))},"
                f" telegago_channels: {len(search_results.get('telegago'))}"
            )
    except Exception as e:
        logger.error(e)
        raise e
    except TelegramBadRequest:
        pass
    return search_results
