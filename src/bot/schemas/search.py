from pydantic import BaseModel, Field


class SearchQueryRequest(BaseModel):
    level1: list[str]
    level2: list[str] | list[None] = Field([None])
    level3: list[str] | list[None] = Field([None])


class SearchQuery(BaseModel):
    country: str | None
    city: str | None = None
    category: str | None = None
