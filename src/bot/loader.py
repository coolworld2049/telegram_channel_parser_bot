from aiogram import Bot
from redis.asyncio import Redis
from selenium.webdriver.chrome.options import Options

from core.settings import get_settings

bot = Bot(get_settings().BOT_TOKEN, parse_mode="HTML")
redis = Redis.from_url(get_settings().redis_url)

options = Options()
options.add_argument("--headless")  # Enable headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--headless")
options.add_argument("--remote-allow-origins=*")
