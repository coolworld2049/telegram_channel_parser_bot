from aiogram import Dispatcher
from loguru import logger

from settings import get_settings
from handlers import main
from loader import bot
from bot.userbot import userbot, userbot_connect  # noqa


async def startup_bot(dp: Dispatcher) -> None:
    # await userbot_connect()
    await bot.delete_my_commands()
    await bot.set_my_commands(get_settings().BOT_COMMANDS)
    dp.include_routers(main.router)
    logger.info("Startup bot")
    return bot


async def shutdown_bot(dp: Dispatcher) -> None:
    await dp.storage.close()
    logger.info("Shutdown bot")
