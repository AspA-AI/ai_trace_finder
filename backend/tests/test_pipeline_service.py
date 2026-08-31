from datetime import datetime, timezone

import pytest

from app.evidence_pipeline.contracts.inputs import PersonClues
from app.evidence_pipeline.contracts.search import SearchResult
from app.evidence_pipeline.orchestration.service import EvidencePipelineService
from app.evidence_pipeline.persistence.in_memory import InMemoryEvidenceRepository


class FakeDiscovery:
    name = "fake"

    async def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        return [
            SearchResult(
                url="https://example.com/profile",
                title="Example profile",
                snippet="Public profile",
                source_provider=self.name,
                discovered_at=datetime.now(timezone.utc),
            )
        ]


class FakeRetriever:
    def supports(self, url: str) -> bool:
        return url.startswith("https://example.com")

    async def fetch(self, url: str, investigation_id: str):
        from hashlib import sha256
        from app.evidence_pipeline.contracts.evidence import RawSource, SourceType

        return RawSource(
            source_id="src_test",
            investigation_id=investigation_id,
            url=url,
            source_type=SourceType.WEBPAGE,
            domain="example.com",
            retrieval_method="fake",
            http_status=200,
            retrieved_at=datetime.now(timezone.utc),
            content="Public profile",
            content_hash=sha256(b"Public profile").hexdigest(),
            provider="fake",
        )


@pytest.mark.asyncio
async def test_pipeline_deduplicates_discovered_urls() -> None:
    service = EvidencePipelineService(FakeDiscovery(), [FakeRetriever()], InMemoryEvidenceRepository())
    result = await service.run(PersonClues(name="Jane Doe"))
    assert len(result["discovered_sources"]) == 1


@pytest.mark.asyncio
async def test_pipeline_records_replayable_trajectory() -> None:
    service = EvidencePipelineService(FakeDiscovery(), [FakeRetriever()], InMemoryEvidenceRepository())
    result = await service.run(PersonClues(name="Jane Doe"))

    trajectory = result["trajectory"]
    assert trajectory[0]["stage"] == "planning"
    assert any(item["action"] == "search_query" and item["status"] == "completed" for item in trajectory)
    assert any(item["action"] == "evaluated_source" for item in trajectory)
    assert any(item["action"] == "skipped_source" and item["stage"] == "extraction" for item in trajectory)
    assert trajectory[-1]["action"] == "completed_run"
    artifact = result["trajectory_artifact"]
    assert artifact["run_id"] == result["run_id"]
    assert artifact["path"]
