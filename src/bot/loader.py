from aiogram import Bot
from fake_useragent import FakeUserAgent
from redis.asyncio import Redis
from selenium.webdriver.chrome.options import Options

from settings import get_settings

redis = Redis.from_url(get_settings().redis_url)

bot = Bot(get_settings().BOT_TOKEN, parse_mode="HTML")

user_agent = FakeUserAgent()
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
