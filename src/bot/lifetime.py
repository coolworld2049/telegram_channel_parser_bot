from aiogram import Dispatcher
from loguru import logger

from core.settings import get_settings
from handlers import main
from loader import bot, userbot


async def startup_bot(dp: Dispatcher) -> None:
    try:
        await userbot.start()
    except AttributeError as e:
        logger.warning(e)
    await bot.delete_my_commands()
    await bot.set_my_commands(get_settings().BOT_COMMANDS)
    dp.include_routers(main.router)
    logger.info("Startup bot")
    return bot


async def shutdown_bot(dp: Dispatcher) -> None:
    await dp.storage.close()
    logger.info("Shutdown bot")
