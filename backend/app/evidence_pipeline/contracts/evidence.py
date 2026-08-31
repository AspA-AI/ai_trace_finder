from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class SourceType(StrEnum):
    WEBPAGE = "webpage"
    GITHUB = "github"
    SEARCH_RESULT = "search_result"
    PDF = "pdf"
    OTHER = "other"


class RawSource(BaseModel):
    """Evidence captured before interpretation or identity resolution."""

    source_id: str
    investigation_id: str
    url: HttpUrl
    canonical_url: HttpUrl | None = None
    source_type: SourceType
    domain: str
    retrieval_method: str
    http_status: int | None = None
    retrieved_at: datetime
    published_at: datetime | None = None
    raw_content: str = ""
    content: str = ""
    content_hash: str
    provider: str
    parent_source_id: str | None = None
    retrieval_error: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
    relevance_score: float | None = None
    relevance_reasons: list[str] = Field(default_factory=list)
    is_relevant: bool | None = None


class Observation(BaseModel):
    """A source-grounded observation; it is not an identity merge."""

    observation_id: str
    source_id: str
    subject_text: str | None = None
    predicate: str
    object_text: str | None = None
    object_type: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    observed_at: datetime
    source_published_at: datetime | None = None
    quote: str | None = None
    source_url: HttpUrl
    extraction_model: str
    extraction_version: str
