def generate_search_queries(*lists: list[str]):
    """

    :param lists: e.g [['qwe', 'fgh', 'vbn'], ['rty','yui','efv']]
    :return:
    """
    if not lists:
        return []
    concatenated_strings = [""]
    for lst in lists:
        temp_concatenated_strings = []
        for item in lst:
            for concat_str in concatenated_strings:
                if item and item != "":
                    temp_concatenated_strings.append(f"{concat_str} {item}")
        temp_concatenated_strings = list(
            map(lambda x: str(x).lstrip(), temp_concatenated_strings)
        )
        concatenated_strings = temp_concatenated_strings
    concatenated_strings.sort()
    return concatenated_strings
