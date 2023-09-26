import asyncio
from urllib.parse import urlsplit

import aiohttp
from aiogram import types
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from fake_useragent import UserAgent
from loguru import logger
from tqdm.contrib.telegram import tqdm

from bot.parser.query_builder import get_code_by_region
from bot.settings import get_settings


async def filter_parsing_result(
    url: str,
    min_subscribers: int = None,
    retries: int = 3,
    **kwargs,
):
    user_agent = UserAgent()
    headers = {
        "User-Agent": user_agent.random,
    }
    new_url = url.replace("t.me/", "t.me/s/")
    source_html = None
    try:
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                source_html = await response.text()
    except Exception as e:
        logger.error(f"{url}. An error occurred: {e}")
        if retries <= 0:
            return False
        logger.info(f"{url}. Retry")
        await asyncio.sleep(abs(1 - retries) + 1)
        await filter_parsing_result(
            url,
            min_subscribers=min_subscribers,
            retries=retries - 1,
        )
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
        logger.debug(
            {
                "url": url,
                "text": text,
                "count": subs_counter,
            },
        )
        if subs_counter >= min_subscribers:
            return True
        else:
            return False
    except Exception as e:  # noqa
        return False


async def ddg_parsing(
    query: tuple[str, str],
    retries: int = 5,
    timeout: float = 10,
    search_limit=6,
    **kwargs,
):
    dork = query[0]
    q = query[1]
    region_code = "wt-wt"
    try:
        if kwargs.get("region_name"):
            region_code = get_code_by_region().get(kwargs.get("region_name"))
    except:  # noqa
        pass
    rows: list[tuple] = []
    unique_result = set()
    try:
        with DDGS(headers={"User-Agent": UserAgent().random}, timeout=timeout) as ddgs:
            for i, r in enumerate(
                ddgs.text(
                    f"{dork} {q}",
                    safesearch="moderate",
                    backend="api",
                    region=region_code,
                )
            ):
                if i == search_limit:
                    break
                usp = urlsplit(r["href"])
                if usp.query:
                    usp = urlsplit(usp.geturl().replace(f"?{usp.query}", ""))
                unique_result.add(usp.geturl())
                rows.append(
                    (
                        q,
                        dork,
                        *list(r.values()),
                    )
                )
        logger.info(f"Unique links number: {len(unique_result)}")
        return rows, unique_result
    except Exception as e:
        logger.error(f"query {query}. Exception: {e}")
        if retries <= 0:
            logger.exception(e)
            raise e
        logger.info(f"query {query}. Retry")
        await asyncio.sleep(timeout)
        await ddg_parsing(query, retries - 1, timeout + 1, **kwargs)


async def ddg_parsing_handler(
    user: types.User,
    queries: list[tuple[str, str]],
    min_subscribers: int,
    region_name: str,
):
    values = [["query", "dork", "title", "href", "body"]]
    results = set()
    for i, query in tqdm(  # noqa
        enumerate(queries),
        total=len(queries),
        token=get_settings().BOT_TOKEN,
        chat_id=user.id,
    ):
        logger.info(
            f"INDEX {i}. Query `{query[1]}'. Region '{region_name}'. Min subscribers '{min_subscribers}'"
        )
        try:
            rows, unique_result = await ddg_parsing(
                query,
                min_subscribers=min_subscribers,
                region_name=region_name,
            )
            for j, unique_url in enumerate(unique_result):
                filter_result = await filter_parsing_result(
                    unique_url, min_subscribers=min_subscribers
                )
                log_msg = {
                    "url": unique_url,
                    "filter": {"min_subscribers": min_subscribers},
                    "filter_result": filter_result,
                }
                if not filter_result:
                    results.discard(unique_url)
                    log_msg.update({"action": "DISCARD"})
                    logger.debug(log_msg)
                else:
                    results.add(unique_url)
                    values.append(rows)
                    log_msg.update({"action": "ADD"})
                    logger.debug(log_msg)
            logger.info(f"Total unique links: {len(results)}")
        except Exception as e:
            logger.error(e)

    return results, values
