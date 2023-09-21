import random
import time
import urllib
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from loguru import logger
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


def extract_html(driver, solver=None, timeout=True, *, url):
    try:
        logger.debug(f"Goto: {url}")
        delay = random.randint(1, random.randint(2, 3)) / 10
        logger.debug(f"delay {delay} sec")
        not timeout or time.sleep(delay)
        driver.get(url=url)
        source_html = driver.page_source
        logger.debug(f"t.me in source_html: {'t.me' in source_html}")
        if solver:
            try:
                recaptcha_iframe = driver.find_element(
                    By.XPATH, '//iframe[@title="reCAPTCHA"]'
                )
                logger.warning(f"reCAPTCHA {recaptcha_iframe}")
                solver.click_recaptcha_v2(iframe=recaptcha_iframe)
                logger.info("reCAPTCHA solved")
                not timeout or time.sleep(random.randint(2, 4) / 10)
                driver.get(url=url)
            except NoSuchElementException as e:
                pass
        return source_html
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e


def parse_lyzem_page(html):
    soup = BeautifulSoup(html, "lxml")
    links = soup.find_all("p", attrs={"class", "search-result-title"})
    channels = []
    for link in links:
        try:
            element_classes = link["class"]
            if "ann" in element_classes:
                continue
            path_url = link.find_next("a").get("href")
            if path_url not in channels:
                channels.append(path_url)
        except KeyError:
            continue
    return channels


def search_channels_lyzem(driver, query: str, limit, max_page_number, per_page):
    base_url = "https://lyzem.com/search?f=channels&l=%3Aru&per-page=100&q="
    base_url = base_url.replace("&per-page=100", f"&per-page={per_page}")
    initial_request_url = base_url + urllib.parse.quote(query)
    logger.debug(f"Lyzem initial request url {initial_request_url}")

    source_html = extract_html(driver, url=initial_request_url)
    page_channels = parse_lyzem_page(source_html)
    all_channels = page_channels

    if len(all_channels) >= limit:
        return all_channels[:limit]

    soup = BeautifulSoup(source_html, "lxml")
    cursor_div = soup.find_all("div", {"class": "pager"})
    logger.debug(cursor_div)
    try:
        num_pages = len(cursor_div[0].find_all("li"))
        if num_pages > max_page_number:
            num_pages = max_page_number
    except IndexError:
        num_pages = 0
        pass

    for i in range(num_pages):
        request_url = initial_request_url + "&p=" + str(i + 1)
        logger.debug(f"Lyzem request url {request_url}; Channels: {len(all_channels)}")
        source_html = extract_html(driver, url=request_url)
        page_channels = parse_lyzem_page(source_html)
        for channel in page_channels:
            if channel not in all_channels:
                all_channels.append(channel)
        if len(all_channels) >= limit:
            return all_channels[:limit]
    logger.debug({"query": query, "channels": len(all_channels)})
    return all_channels
