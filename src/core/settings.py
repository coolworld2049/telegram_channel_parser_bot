import pathlib
from functools import lru_cache
from typing import Optional

from aiogram.types import BotCommand
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class BotSettings(BaseSettings):
    BOT_TOKEN: str
    BOT_COMMANDS: list[BotCommand] = [
        BotCommand(command="/start", description="Start bot"),
        BotCommand(
            command="/search", description="Search telegram channels by keywords"
        ),
        BotCommand(command="/set_session", description="Set pyrogram session"),
    ]
    BOT_ACL: list[int] = []
    BOT_ACL_ENABLED: bool = False


class UserBotSettings(BaseSettings):
    API_ID: int = None
    API_HASH: str = None
    PHONE_NUMBER: str = None
    SESSION_STRING_FILE: str = "bot/pyrogram.txt"

    @property
    def session_string(self):
        try:
            return (
                pathlib.Path(__file__)
                .parent.parent.joinpath(pathlib.Path(self.SESSION_STRING_FILE))
                .open("r")
                .readline()
            )
        except FileNotFoundError:
            return None


class SeleniumSettings(BaseSettings):
    SE_WEBDRIVER_URL: str = "http://localhost:4444"


class BotRedisSettings(BaseSettings):
    REDIS_MASTER_HOST: str = "127.0.0.1"
    REDIS_MASTER_PORT_NUMBER: Optional[int] = 6379
    REDIS_USERNAME: Optional[str] = "default"
    REDIS_PASSWORD: Optional[str] = None

    @property
    def redis_url(self):
        password = (
            f"{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}@"
            if self.REDIS_PASSWORD
            else ""
        )
        return f"redis://{password}{self.REDIS_MASTER_HOST}:{self.REDIS_MASTER_PORT_NUMBER}/0"


class Settings(BotSettings, BotRedisSettings, UserBotSettings, SeleniumSettings):
    LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    config = Settings
    return config()
