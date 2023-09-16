import pathlib
from functools import lru_cache
from typing import Optional, Literal

from aiogram.types import BotCommand
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class BotSettings(BaseSettings):
    BOT_TOKEN: str
    BOT_RUN_MODE: Literal["webhook", "polling"] = "polling"
    BOT_COMMANDS: list[BotCommand] = [
        BotCommand(command="/start", description="start bot"),
    ]
    WEBHOOK_URL: Optional[str] = None
    WEB_APP_HOST: Optional[str] = "0.0.0.0"
    WEB_APP_PORT: Optional[int] = 8000

    @property
    def webhook_url(self):
        return f"{self.WEBHOOK_URL}/telegram_bot{self.BOT_TOKEN}"


class RedisSettings(BaseSettings):
    REDIS_MASTER_HOST: str
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


class Settings(BotSettings, RedisSettings):
    LOG_FILE_PATH: Optional[str] = f"{pathlib.Path(__file__).parent.parent}/.logs"
    LOGGING_LEVEL: Optional[str] = "INFO"
    TZ: Optional[str] = "Europe/Moscow"


@lru_cache
def get_settings() -> Settings:
    config = Settings
    return config()
