import random
import time
import urllib
from pprint import pprint
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from loguru import logger
from selenium.webdriver.common.by import By

TELEGAGO_BASE_URL = "https://cse.google.com/cse?q=+&cx=006368593537057042503:efxu7xprihg#gsc.tab=0&gsc.ref=more%3Apublic&gsc.q="
LYZEM_BASE_URL = "https://lyzem.com/search?f=channels&l=%3Aen&per-page=100&q="


# extracts the html from a URL using the requests_html library (supports JS)
# async def extract_html(url):
#     session = AsyncHTMLSession()
#     response = await session.get(url)  # noqa
#     if javascript_enabled:
#         await response.html.arender()
#         source_html = response.html.html
#         await session.close()
#         return source_html
#     else:
#         await session.close()
#         return response.html.html


def extract_html(driver, solver, url):
    # Set up Chrome options for headless browsing
    try:
        logger.debug(f"Goto: {url}")
        # Navigate to the URL
        time.sleep(random.randint(10, random.randint(20, 50)) / 10)
        driver.get(url=url)
        try:
            recaptcha_iframe = driver.find_element(
                By.XPATH, '//iframe[@title="reCAPTCHA"]'
            )
            solver.click_recaptcha_v2(iframe=recaptcha_iframe)
            logger.info("reCAPTCHA: click_recaptcha_v2")
        except:
            pass

        # Get the page's HTML source after JavaScript execution
        source_html = driver.page_source

        return source_html
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


# method to parse the HTML from the Lyzem page
def parse_lyzem_page(html):
    soup = BeautifulSoup(html, "lxml")
    links = soup.find_all("p", attrs={"class", "search-result-title"})
    channels = []
    for link in links:
        try:
            element_classes = link["class"]
            # if they have this element this means the result is an advertisement
            # we dont want these
            if "ann" in element_classes:
                continue
            path_url = link.find_next("a").get("href")
            channel_name = path_url.split("?")[0].split("/")[-1]
            if channel_name not in channels:
                channels.append(channel_name)
        except KeyError:
            continue
    return channels


def search_channels_lyzem(driver, solver, query: str, limit=100):
    initial_request_url = LYZEM_BASE_URL + urllib.parse.quote(query)
    # logger.debug("Lyzem request url {}".format(initial_request_url))

    # extract channels from initial page
    source_html = extract_html(driver, solver, initial_request_url)
    page_channels = parse_lyzem_page(source_html)
    all_channels = page_channels

    # if reached limit return the channels
    if len(all_channels) >= limit:
        return all_channels[:limit]

    # otherwise we need to go to next pages
    # find the number of pages from the html
    soup = BeautifulSoup(source_html, "lxml")
    cursor_div = soup.find_all("nav", {"class": "pages"})
    try:
        num_pages = len(cursor_div[0].find_all("li"))
    except IndexError:
        num_pages = 0
        pass

    # then iterate over all pages to extract all channels
    for i in range(num_pages):
        request_url = initial_request_url + "&p=" + str(i + 1)
        logger.debug(f"Lyzem request url {request_url}; Channels: {len(all_channels)}")
        source_html = extract_html(driver, solver, request_url)
        page_channels = parse_lyzem_page(source_html)
        for channel in page_channels:
            if channel not in all_channels:
                all_channels.append(channel)
        if len(all_channels) >= limit:
            return all_channels[:limit]
    return all_channels


# method to parse the HTML from the telegago page
def parse_telegago_page(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        links = soup.find_all("a", attrs={"class", "gs-title"})
        channels = []
        for link in links:
            try:
                path_url = urlparse(link["href"]).path
                if path_url.startswith("/s/"):
                    if path_url.count("/") == 2:
                        channel_name = path_url.split("/")[-1]
                    else:
                        channel_name = path_url.split("/")[-2]
                else:
                    channel_name = path_url.split("/")[1]
                if channel_name not in channels:
                    channels.append(channel_name)
            except KeyError:
                continue
    except Exception as e:
        logger.error(html)
        raise e
    return channels


def search_channels_telegago(driver, solver, query: str, limit=100):
    initial_request_url = TELEGAGO_BASE_URL + urllib.parse.quote(query)
    # logger.debug("Telegago request url {}".format(initial_request_url))

    # extract channels from initial page
    source_html = extract_html(driver, solver, initial_request_url)
    page_channels = parse_telegago_page(source_html)
    all_channels = page_channels

    # if reached limit return the channels
    if len(all_channels) >= limit:
        return all_channels[:limit]

    # otherwise we need to go to next pages
    # find the number of pages from the html
    soup = BeautifulSoup(source_html, "lxml")
    cursor_div = soup.find_all("div", {"class": "gsc-cursor"})
    try:
        num_pages = len(cursor_div[0].find_all("div"))
    except IndexError:
        num_pages = 0
        pass

    # then iterate over all pages to extract all channels
    for i in range(num_pages):
        request_url = initial_request_url + "&gsc.page=" + str(i + 1) + "&gsc.sort="
        logger.debug(
            f"Telegago request url {request_url}; Channels: {len(all_channels)}"
        )
        source_html = extract_html(driver, solver, request_url)
        page_channels = parse_telegago_page(source_html)
        for channel in page_channels:
            if channel not in all_channels:
                all_channels.append(channel)
        if len(all_channels) >= limit:
            return all_channels[:limit]
    return all_channels


if __name__ == "__main__":
    # print("search_channels_lyzem")
    # res = search_channels_lyzem("Чат южная корея")
    # pprint(res)

    print("search_channels_telegago")
    res = search_channels_telegago("Чат южная корея")
    pprint(res)
