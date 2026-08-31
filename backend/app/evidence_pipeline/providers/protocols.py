from typing import Protocol

from app.evidence_pipeline.contracts.evidence import RawSource
from app.evidence_pipeline.contracts.search import SearchResult


class DiscoveryProvider(Protocol):
    name: str

    async def search(self, query: str, limit: int = 10) -> list[SearchResult]: ...


class SourceRetriever(Protocol):
    name: str

    def supports(self, url: str) -> bool: ...

    async def fetch(self, url: str, investigation_id: str) -> RawSource: ...
