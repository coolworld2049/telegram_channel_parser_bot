import time
from typing import List

from loguru import logger

from bot.schemas.search import SearchQuery


def generate_search_queries(*levels: list):
    if len(levels) < 1:
        return None
    level1 = []
    level2 = []
    level3 = []
    try:
        level1 = levels[0]
        level2 = levels[1]
        level3 = levels[2]
    except:
        pass
    # Rule 1: Generate queries with only level 1 keywords
    if len(level1) > 0:
        for country in level1:
            yield SearchQuery(country=country, city=None, category=None)

    # Rule 2: Generate queries with only level 2 keywords
    if len(level2) > 0:
        for city in level2:
            yield SearchQuery(country=None, city=city, category=None)

    # Rule 3: Generate queries by combining level 1 and level 2 keywords
    if len(level1) > 0 and len(level2) > 0:
        for country in level1:
            for city in level2:
                yield SearchQuery(country=country, city=city, category=None)

    # Rule 4: Generate queries by combining level 1, level 2, and level 3 keywords
    if len(level1) > 0 and len(level2) > 0 and len(level3) > 0:
        for country in level1:
            for city in level2:
                for category in level3:
                    yield SearchQuery(country=country, city=city, category=category)


if __name__ == "__main__":
    # Example usage
    level1_keywords = ["южная корея", "корея"]
    level2_keywords = ["сеул", "бусан", "инчон", "андон", "кёнджу", "тэгу", "кванджу"]
    level3_keywords = [
        "работа",
        "туризм",
        "хвасон",
        "виза",
        "g1",
        "страхование",
        "страховка",
        "караоке",
        "ктв",
        "ktv",
        "солнечные батареи",
        "кёнгидо",
        "Канвондо Янъян",
    ]
    s = time.time()
    for query in generate_search_queries(
        level1_keywords, level2_keywords, level3_keywords
    ):
        logger.debug(
            f"Country: {query.country} City: {query.city} Category: {query.category}"
        )
    e = time.time()
    print(f"{e - s}")