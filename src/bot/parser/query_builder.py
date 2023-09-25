from functools import lru_cache

data_list = [
    "Arabia",
    "Arabia (en)",
    "Argentina",
    "Australia",
    "Austria",
    "Belgium (fr)",
    "Belgium (nl)",
    "Brazil",
    "Bulgaria",
    "Canada",
    "Canada (fr)",
    "Catalan",
    "Chile",
    "China",
    "Colombia",
    "Croatia",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hong Kong",
    "Hungary",
    "India",
    "Indonesia",
    "Indonesia (en)",
    "Ireland",
    "Israel",
    "Italy",
    "Japan",
    "Korea",
    "Latvia",
    "Lithuania",
    "Latin America",
    "Malaysia",
    "Malaysia (en)",
    "Mexico",
    "Netherlands",
    "New Zealand",
    "Norway",
    "Peru",
    "Philippines",
    "Philippines (tl)",
    "Poland",
    "Portugal",
    "Romania",
    "Russia",
    "Singapore",
    "Slovak Republic",
    "Slovenia",
    "South Africa",
    "Spain",
    "Sweden",
    "Switzerland (de)",
    "Switzerland (fr)",
    "Switzerland (it)",
    "Taiwan",
    "Thailand",
    "Turkey",
    "Ukraine",
    "United Kingdom",
    "United States",
    "United States (es)",
    "Venezuela",
    "Vietnam",
    "No region",
]

code_list = [
    "xa-ar",
    "xa-en",
    "ar-es",
    "au-en",
    "at-de",
    "be-fr",
    "be-nl",
    "br-pt",
    "bg-bg",
    "ca-en",
    "ca-fr",
    "ct-ca",
    "cl-es",
    "cn-zh",
    "co-es",
    "hr-hr",
    "cz-cs",
    "dk-da",
    "ee-et",
    "fi-fi",
    "fr-fr",
    "de-de",
    "gr-el",
    "hk-tzh",
    "hu-hu",
    "in-en",
    "id-id",
    "id-en",
    "ie-en",
    "il-he",
    "it-it",
    "jp-jp",
    "kr-kr",
    "lv-lv",
    "lt-lt",
    "xl-es",
    "my-ms",
    "my-en",
    "mx-es",
    "nl-nl",
    "nz-en",
    "no-no",
    "pe-es",
    "ph-en",
    "ph-tl",
    "pl-pl",
    "pt-pt",
    "ro-ro",
    "ru-ru",
    "sg-en",
    "sk-sk",
    "sl-sl",
    "za-en",
    "es-es",
    "se-sv",
    "ch-de",
    "ch-fr",
    "ch-it",
    "tw-tzh",
    "th-th",
    "tr-tr",
    "ua-uk",
    "uk-en",
    "us-en",
    "ue-es",
    "ve-es",
    "vn-vi",
    "wt-wt",
]


@lru_cache
def get_code_by_region():
    return dict(zip(data_list, code_list))


@lru_cache
def get_region_by_code():
    return dict(zip(code_list, data_list))


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
