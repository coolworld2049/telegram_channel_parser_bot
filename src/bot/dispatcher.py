import pathlib

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from bot.middleware.callback import CallbackAnswerMiddleware
from loader import redis

dp = Dispatcher(
    storage=RedisStorage(redis),
    name=pathlib.Path(__file__).name,
)
dp.callback_query.middleware(CallbackAnswerMiddleware())
