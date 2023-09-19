import pathlib

import pyrogram
from loguru import logger

userbot = pyrogram.Client("pyrogram")


async def userbot_connect():
    session_string_p = pathlib.Path(__file__).parent.joinpath(
        pathlib.Path("pyrogram.txt")
    )
    if session_string_p.exists():
        userbot.session_string = session_string_p.open("r").read().strip()
        userbot.in_memory = True
        try:
            await userbot.connect()
            await userbot.get_me()
            session = await userbot.export_session_string()
            session_string_p.open("w").write(str(session))
            logger.info("Startup userbot")
        except Exception as e:
            logger.warning(e)
    else:
        logger.warning(f"FileNotFound: {session_string_p.absolute()}")
