import asyncio

from loguru import logger

from bot.dispatcher import dp
from bot.lifetime import startup_bot, shutdown_bot
from loader import bot
from userbot.lifetime import startup_userbot, shutdown_userbot


async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await startup_bot(dp)
        await startup_userbot(bot)
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(e)
    finally:
        await shutdown_userbot(bot)
        await shutdown_bot(dp)


if __name__ == "__main__":
    asyncio.run(main())
