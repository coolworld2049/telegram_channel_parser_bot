import pathlib

import uvicorn
from fastapi import FastAPI
from loguru import logger
from telethon import TelegramClient

from core.settings import get_settings
from userbot.routes.telegram import search, auth

app = FastAPI(
    title=pathlib.Path(__file__).parent.parent.parent.name,
)
client = TelegramClient(
    "my",
    get_settings().API_ID,
    get_settings().API_HASH,
)


@app.on_event("startup")
async def startup():
    # await startup_userbot(app)
    app.include_router(search.router)
    app.include_router(auth.router)
    logger.info(f"Startup")


@app.on_event("shutdown")
async def shutdown():
    # await shutdown_userbot(app)
    logger.info("Shutdown")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, reload=False)
