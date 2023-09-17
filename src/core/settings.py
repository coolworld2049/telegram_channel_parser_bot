import pathlib
from functools import lru_cache
from typing import Optional, Union, List

from aiogram.types import BotCommand
from dotenv import load_dotenv
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

load_dotenv()


class BotSettings(BaseSettings):
    BOT_TOKEN: str
    BOT_COMMANDS: list[BotCommand] = [
        BotCommand(command="/start", description="Start bot"),
        BotCommand(command="/auth", description="Log in telegram account"),
        BotCommand(
            command="/search", description="Search telegram channels by keywords"
        ),
    ]
    USERBOT_API_BASE_URL: str = "http://localhost:8000"


class UserBotSettings(BaseSettings):
    API_ID: int
    API_HASH: str
    PHONE_NUMBER: str
    HOST: str = "localhost"
    PORT: int = 8000
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost"]

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


class BotRedisSettings(BaseSettings):
    REDIS_MASTER_HOST: str = "localhost"
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


class Settings(BotSettings, BotRedisSettings, UserBotSettings):
    LOG_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    LOGGING_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    config = Settings
    return config()
