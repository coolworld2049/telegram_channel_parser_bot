from loguru import logger


def get_generated_search_queries(*lists):
    if not lists:
        return []

    concatenated_strings = [""]

    for l, lst in enumerate(lists):
        temp_concatenated_strings = []

        for item in lst:
            for concat_str in concatenated_strings:
                if item and item != "":
                    temp_concatenated_strings.append(f"{concat_str} {item}")
        temp_concatenated_strings = list(
            map(lambda x: str(x).lstrip(), temp_concatenated_strings)
        )
        logger.debug(f"Current list index {l}")
        concatenated_strings = temp_concatenated_strings
    concatenated_strings.sort()
    logger.debug(f"End")
    return concatenated_strings


if __name__ == "__main__":
    level1_keywords = [x.strip() for x in "Турция".split(",")]
    level2_keywords = [
        x.strip() for x in "Анталья, Анталия, Стамбул, Измир, Алания".split(",")
    ]
    level3_keywords = [
        x.strip() for x in "русскоязычные, чат, форум, знакомства, общение".split(",")
    ]
    result = get_generated_search_queries(
        level1_keywords, level2_keywords, level3_keywords
    )
    for concatenated_str in result:
        print(concatenated_str)
