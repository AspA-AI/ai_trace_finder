from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class SearchQuery(BaseModel):
    query: str
    source_filter: str | None = None
    rationale: str | None = None


class SearchResult(BaseModel):
    url: HttpUrl
    title: str | None = None
    snippet: str | None = None
    source_provider: str
    discovered_at: datetime


class DiscoveryResponse(BaseModel):
    query: SearchQuery
    results: list[SearchResult] = Field(default_factory=list)
    error: str | None = None
