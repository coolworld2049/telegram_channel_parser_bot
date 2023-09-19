import asyncio
import pathlib
import time

import pyrogram
from loguru import logger

userbot = pyrogram.Client("pyrogram")

session_string_p = pathlib.Path("pyrogram.txt")
if session_string_p.exists():
    userbot.session_string = session_string_p.open("r").read().strip()
    userbot.in_memory = True
    try:
        time.sleep(0.5)
        asyncio.run(userbot.start())
    except Exception as e:
        logger.warning(e)
else:
    logger.warning(f"FileNotFound: {session_string_p.absolute()}")
