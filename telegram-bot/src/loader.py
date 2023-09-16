from aiogram import Bot
from redis.asyncio import Redis

from settings import get_settings

bot = Bot(get_settings().BOT_TOKEN, parse_mode="HTML")
redis = Redis.from_url(get_settings().redis_url)
