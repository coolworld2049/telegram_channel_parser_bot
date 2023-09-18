from pydantic import BaseModel, Field


class SearchQueryRequest(BaseModel):
    level1: list[str]
    level2: list[str] | list[None] = Field([None])
    level3: list[str] | list[None] = Field([None])


class SearchRequest(SearchQueryRequest):
    limit: int | None = Field(100)
    delay: float | None = Field(
        0.1, le=5, description="Delay between requests to Telegram server in seconds"
    )


class SearchQuery(BaseModel):
    country: str | None
    city: str | None = None
    category: str | None = None
