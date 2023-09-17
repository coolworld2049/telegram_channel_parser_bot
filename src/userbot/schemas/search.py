from typing import Any

from pydantic import BaseModel, Field


class SearchQueryRequest(BaseModel):
    level1: list[str]
    level2: list[str] | list[None] = Field([None])
    level3: list[str] | list[None] = Field([None])


class TelethonSearchRequest(SearchQueryRequest):
    limit: int | None = Field(100)
    delay: float | None = Field(
        0.1, le=5, description="Delay between requests to Telegram server in seconds"
    )


class GoogleSearchRequest(SearchQueryRequest):
    tld: str = "com"
    lang: str = "en"
    tbs: str = "0"
    safe: str = "off"
    num: int = 10
    start: int = 0
    stop: int = Field(None)
    pause: float = 2.0
    country: str = ""
    extra_params: dict[str, Any] | None = Field(None)
    user_agent: str = Field(None)
    verify_ssl: bool = True


class SearchQuery(BaseModel):
    country: str | None
    city: str | None = None
    category: str | None = None
