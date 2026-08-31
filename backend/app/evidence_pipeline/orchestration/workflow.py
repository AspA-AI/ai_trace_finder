from dataclasses import dataclass, field

from app.evidence_pipeline.contracts.evidence import RawSource
from app.evidence_pipeline.contracts.inputs import PersonClues
from app.evidence_pipeline.contracts.search import SearchQuery, SearchResult


@dataclass
class EvidencePipelineRun:
    """Explicit state boundary for one evidence collection run."""

    investigation_id: str
    clues: PersonClues
    queries: list[SearchQuery] = field(default_factory=list)
    discovered_results: list[SearchResult] = field(default_factory=list)
    raw_sources: list[RawSource] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
