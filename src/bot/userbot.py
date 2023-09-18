import asyncio
import pathlib

import pyrogram
from loguru import logger

userbot = pyrogram.Client("pyrogram")

session_string_p = pathlib.Path("pyrogram.txt")
session_string = session_string_p.open("r").read().strip()
if session_string_p.exists():
    userbot.session_string = session_string
    userbot.in_memory = True
    try:
        asyncio.run(userbot.start())
    except Exception as e:
        logger.warning(e)
