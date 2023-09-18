from aiogram import Bot
from fake_useragent import UserAgent
from redis.asyncio import Redis
from selenium.webdriver.chrome.options import Options

from core.settings import get_settings

bot = Bot(get_settings().BOT_TOKEN, parse_mode="HTML")
redis = Redis.from_url(get_settings().redis_url)

user_agent = UserAgent()
chrome_options = Options()

chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-extensions")
