from loguru import logger
from pyrogram import Client

from settings import get_settings


async def startup_userbot(aiogram_bot):
    client = userbot = Client(
        "my", in_memory=True, session_string=get_settings().session_string
    )
    if not client:
        raise ValueError(client)
    aiogram_bot.client = client
    logger.info("Startup")
    return aiogram_bot


async def shutdown_userbot(aiogram_bot):
    await aiogram_bot.client.stop()
    logger.info("Shutdown")
