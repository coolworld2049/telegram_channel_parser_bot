import asyncio
import sys

from loguru import logger

from core.settings import get_settings
from dispatcher import dp
from lifetime import startup_bot, shutdown_bot
from loader import bot

logger.remove()
logger.add(
    sys.stdout,
    level=get_settings().LOG_LEVEL,
)
logger.add(
    ".logs/access.log",
    level=get_settings().LOG_LEVEL,
    serialize=False,
    backtrace=True,
    encoding="utf-8",
    enqueue=True,
    rotation="32 MB",
    retention="7 days",
)


async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await startup_bot(dp)
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(e)
    finally:
        await shutdown_bot(dp)


if __name__ == "__main__":
    asyncio.run(main())
