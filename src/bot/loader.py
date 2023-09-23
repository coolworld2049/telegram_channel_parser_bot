from aiogram import Bot
from fake_useragent import FakeUserAgent
from redis.asyncio import Redis
from selenium.webdriver.chrome.options import Options

from settings import get_settings

redis = Redis.from_url(get_settings().redis_url)
bot = Bot(get_settings().BOT_TOKEN, parse_mode="HTML")
