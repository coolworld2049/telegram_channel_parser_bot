import pathlib
from urllib.parse import parse_qs

from fp.fp import FreeProxy
from loguru import logger
from search_engine_parser.core.engines.duckduckgo import Search as DDG

from bot.cse.query_builder import get_generated_search_queries

level1_keywords = [x.strip() for x in "Турция".split(",")]
level2_keywords = [
    x.strip()
    for x in "Анталия, Стамбул, Измир, Алания, Бодрум, Ортаджа, Анкара, Газиантеп".split(
        ","
    )
]
level3_keywords = [
    x.strip() for x in "логистика, грузоперевозки, ритейл, бизнес".split(",")
]
search_queries = get_generated_search_queries(level2_keywords, level3_keywords)


search_args = [(f"site:t.me {x}", 1) for x in search_queries[:4]]
ddg_search = DDG()
p = pathlib.Path("output.md").open("w+")


def search(q, retries=3):
    try:
        logger.info(f"{q}. Search")
        ddg_search_results = ddg_search.search(
            *q, cache=False, proxy=FreeProxy(rand=True).get()
        )
        for d in ddg_search_results:
            logger.debug(f"title: {d['title']}, links: {d['links']}")
            qs = parse_qs(d["links"])
            p.write(str(list(parse_qs(d["links"]).values())[0][0]) + "\n")
    except Exception as e:
        if retries <= 0:
            logger.error(e)
            return None
        logger.error(f"{q}. Retry")
        search(q, retries - 1)


for q in search_args:
    search(q)
