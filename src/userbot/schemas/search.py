from pydantic import BaseModel, Field


class TelethonSearchRequest(BaseModel):
    limit: int | None = 50
    delay: float | None = Field(
        0.1, description="Delay between requests to Telegram server in seconds"
    )


class SearchQueryRequest(TelethonSearchRequest):
    level1: list[str]
    level2: list[str] | None = None
    level3: list[str] | None = None


class SearchQuery(BaseModel):
    country: str
    city: str = None
    category: str = None
