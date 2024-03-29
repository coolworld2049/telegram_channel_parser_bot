from aiogram import Dispatcher
from loguru import logger

from handlers import main
from loader import bot
from settings import get_settings


async def startup_bot(dp: Dispatcher) -> None:
    await bot.delete_my_commands()
    await bot.set_my_commands(get_settings().BOT_COMMANDS)
    dp.include_routers(main.router)
    logger.info("Startup bot")
    return bot


async def shutdown_bot(dp: Dispatcher) -> None:
    await dp.storage.close()
    logger.info("Shutdown bot")
