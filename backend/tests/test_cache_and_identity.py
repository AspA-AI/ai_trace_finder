import asyncio
import tempfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from app.evidence_pipeline.contracts.evidence import RawSource, SourceType
from app.evidence_pipeline.persistence.sqlite import SQLiteEvidenceRepository
from app.evidence_pipeline.retrieval.relevance import matches_identity
from app.evidence_pipeline.contracts.inputs import PersonClues


def test_sqlite_cache_accepts_naive_fetched_at() -> None:
    with tempfile.TemporaryDirectory() as directory:
        repository = SQLiteEvidenceRepository(f"sqlite:///{Path(directory) / 'test.db'}")
        source = RawSource(
            source_id="src_cache",
            investigation_id="inv_abc123def456",
            url="https://example.com/profile",
            canonical_url="https://example.com/profile",
            source_type=SourceType.WEBPAGE,
            domain="example.com",
            retrieval_method="test",
            http_status=200,
            retrieved_at=datetime.now(timezone.utc),
            content="hello",
            content_hash=sha256(b"hello").hexdigest(),
            provider="test",
        )
        with repository._connect() as connection:
            connection.execute(
                "INSERT INTO source_cache VALUES (?, ?, ?, ?)",
                (source.source_id, str(source.canonical_url), source.model_dump_json(), "2026-08-31 12:00:00"),
            )
        cached = asyncio.run(repository.get_cached("https://example.com/profile", 24 * 365 * 10))
        assert cached is not None
        assert cached.source_id == "src_cache"


def test_short_name_tokens_do_not_match_identity() -> None:
    clues = PersonClues(name="Al")
    assert matches_identity("Alexander Hamilton biography", clues) is False
    clues = PersonClues(name="Jane Doe")
    assert matches_identity("Jane Doe works in Austin", clues) is True
