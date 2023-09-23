import asyncio
import random
from urllib.parse import urlsplit

import aiohttp
from aiogram import types
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from fake_useragent import FakeUserAgent
from loguru import logger
from tqdm.contrib.telegram import tqdm

from bot.settings import get_settings


async def filter_parsing_result(
    url: str,
    retries: int = 3,
    min_subscribers: int = None,
):
    user_agent = FakeUserAgent()
    headers = {
        "User-Agent": user_agent.random,
    }
    new_url = url.replace("t.me/", "t.me/s/")
    source_html = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                source_html = await response.text()
    except Exception as e:
        logger.error(f"{url}. An error occurred: {e}")
        if retries <= 0:
            return False
        logger.info(f"{url}. Retry")
        await asyncio.sleep(abs(1 - retries) + 1)
        await filter_parsing_result(url, retries - 1, min_subscribers)
    soup = BeautifulSoup(source_html, "lxml")
    try:
        tgme_page_extra = soup.find("div", attrs="tgme_page_extra") or soup.find(
            "div", attrs="tgme_header_counter"
        )
        text = tgme_page_extra.text
        subs_counter = None
        # logger.opt(colors=True).debug(f"url {url}, <yellow>text: {text}</yellow>")

        if "online" in text and "members" in text:
            subs_str = text.split(",")[0].split("members")[0].replace(" ", "")
            subs_counter = int(subs_str)
        if "subscribers" in text:
            subs_str = text.split(" subscribers")[0]
            if "K" in subs_str:
                number = subs_str.split("K")[0]
                subs_counter = int(float(number) * 1000)
            else:
                subs_str = subs_str.replace(" ", "")
                subs_counter = int(subs_str)
        # logger.debug(
        #     {
        #         "url": url,
        #         "filter": {
        #             "min_subscribers": {"lq": min_subscribers},
        #             "subscribers": subs_counter,
        #             "text": text,
        #         },
        #     },
        # )
        if subs_counter >= min_subscribers:
            return True
        else:
            return False
    except Exception as e:  # noqa
        return False


async def ddg_parsing(
    query: str,
    retries: int = 5,
    timeout: float = 10,
    **kwargs,
):
    unique_result = set()
    user_agent = FakeUserAgent()
    headers = {"User-Agent": user_agent.random}
    try:
        logger.info({"query": query})
        search_result = []
        with DDGS(headers=headers, timeout=timeout) as ddgs:
            await asyncio.sleep(0.75)
            logger.debug("sleep 0.75")
            for r in ddgs.text(query, backend=random.choice(["api", "html"])):
                search_result.append(r)
        logger.info({"query": query, "search_result": len(search_result)})
        for sr in search_result[:20]:
            usp = urlsplit(sr["href"])
            if usp.query:
                usp = urlsplit(usp.geturl().replace(f"?{usp.query}", ""))
            url = usp.geturl()
            unique_result.add(url)
        for unique_url in unique_result.copy():
            filter_result = await filter_parsing_result(
                unique_url,
                **kwargs,
            )
            log_msg = {
                "url": unique_url,
                "filter": kwargs,
                "filter_result": filter_result,
            }
            if not filter_result:
                unique_result.discard(unique_url)
                log_msg.update({"action": "DISCARD url from set"})
                logger.debug(log_msg)
            logger.debug(log_msg)
        logger.info(
            {
                "query": query,
                "search_result": len(search_result),
                "unique_filtered_result": len(unique_result),
            }
        )
        return unique_result
    except Exception as e:
        logger.error(f"{query}. Exception: {e}")
        if retries <= 0:
            logger.exception(e)
            raise e
        logger.info(f"{query}. Retry")
        await ddg_parsing(query, retries - 1, timeout + 5, **kwargs)


async def ddg_parsing_handler(
    user: types.User, queries: list[str], min_subscribers: int
):
    result = set()
    for i, query in tqdm(  # noqa
        enumerate(queries),
        total=len(queries),
        token=get_settings().BOT_TOKEN,
        chat_id=user.id,
    ):
        logger.info(f"index {i}. START")
        links = set()
        try:
            links = await ddg_parsing(query, min_subscribers=min_subscribers)
            result = result.union(links)
        except Exception as e:
            logger.error(e)
        logger.info(
            {
                "index": i,
                "query": query,
                "links": len(links) if not links else None,
                "all_links": len(result),
                "min_subscribers": min_subscribers,
            }
        )
        logger.info(f"index {i}. END")
    return result
