import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.ids import parse_utc
from app.evidence_pipeline.contracts.evidence import Observation, RawSource


class SQLiteEvidenceRepository:
    """Small durable repository for the prototype; the contract can map to Postgres later."""

    def __init__(self, database_url: str) -> None:
        path = database_url.removeprefix("sqlite:///")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.sources: dict[str, RawSource] = {}
        self.observations: dict[str, Observation] = {}
        self._init_schema()

    def _connect(self):
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    def _init_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS investigations (
                    investigation_id TEXT PRIMARY KEY,
                    clues_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    investigation_id TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS raw_sources (
                    source_id TEXT PRIMARY KEY,
                    investigation_id TEXT NOT NULL,
                    source_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS observations (
                    observation_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    observation_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS investigation_observations (
                    investigation_id TEXT NOT NULL,
                    observation_id TEXT NOT NULL,
                    observation_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (investigation_id, observation_id)
                );
                CREATE TABLE IF NOT EXISTS source_cache (
                    source_id TEXT PRIMARY KEY,
                    canonical_url TEXT UNIQUE NOT NULL,
                    source_json TEXT NOT NULL,
                    fetched_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS investigation_sources (
                    investigation_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    relevance_score REAL,
                    is_relevant INTEGER NOT NULL,
                    relevance_reasons TEXT NOT NULL,
                    PRIMARY KEY (investigation_id, source_id)
                );
                CREATE TABLE IF NOT EXISTS verification_runs (
                    investigation_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (investigation_id, run_id)
                );
                CREATE TABLE IF NOT EXISTS profiles (
                    investigation_id TEXT PRIMARY KEY,
                    profile_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    async def create_investigation(
        self, investigation_id: str, clues_json: str, created_at: str
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO investigations VALUES (?, ?, ?) ON CONFLICT(investigation_id) DO UPDATE SET clues_json = excluded.clues_json",
                (investigation_id, clues_json, created_at),
            )

    async def save_run(
        self, run_id: str, investigation_id: str, result: dict, created_at: str
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?)",
                (run_id, investigation_id, json.dumps(result), created_at),
            )

    async def save_verification(self, investigation_id: str, run_id: str, result: dict) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO verification_runs VALUES (?, ?, ?, ?)",
                (
                    investigation_id,
                    run_id,
                    json.dumps(result),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def get_verification(self, investigation_id: str, run_id: str | None = None) -> dict | None:
        with self._connect() as connection:
            if run_id:
                row = connection.execute(
                    "SELECT result_json FROM verification_runs WHERE investigation_id = ? AND run_id = ?",
                    (investigation_id, run_id),
                ).fetchone()
            else:
                row = connection.execute(
                    "SELECT result_json FROM verification_runs WHERE investigation_id = ? ORDER BY created_at DESC LIMIT 1",
                    (investigation_id,),
                ).fetchone()
        return json.loads(row[0]) if row else None

    def list_verification_runs(self, investigation_id: str) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT run_id, created_at FROM verification_runs WHERE investigation_id = ? ORDER BY created_at DESC",
                (investigation_id,),
            ).fetchall()
        return [{"run_id": row["run_id"], "created_at": row["created_at"]} for row in rows]

    async def save_profile(self, investigation_id: str, profile: dict) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO profiles VALUES (?, ?, ?)",
                (investigation_id, json.dumps(profile), datetime.now(timezone.utc).isoformat()),
            )

    def get_profile(self, investigation_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute("SELECT profile_json FROM profiles WHERE investigation_id = ?", (investigation_id,)).fetchone()
        return json.loads(row[0]) if row else None

    async def save(self, source: RawSource) -> RawSource:
        self.sources[source.source_id] = source
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO raw_sources VALUES (?, ?, ?, ?)",
                (source.source_id, source.investigation_id, source.model_dump_json(), now),
            )
            connection.execute(
                "INSERT OR REPLACE INTO source_cache VALUES (?, ?, ?, ?)",
                (
                    source.source_id,
                    str(source.canonical_url or source.url),
                    source.model_dump_json(),
                    now,
                ),
            )
        return source

    async def get_cached(self, canonical_url: str, max_age_hours: int):
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT source_json, fetched_at FROM source_cache WHERE canonical_url = ?",
                (canonical_url,),
            ).fetchone()
        if not row:
            return None
        try:
            fetched_at = parse_utc(row["fetched_at"])
        except ValueError:
            return None
        if fetched_at < cutoff:
            return None
        cached = RawSource.model_validate_json(row["source_json"])
        return cached

    async def link_source(
        self,
        investigation_id: str,
        source: RawSource,
        relevance_score: float,
        relevant: bool,
        reasons: list[str],
    ) -> None:
        canonical_url = str(source.canonical_url or source.url)
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO source_cache VALUES (?, ?, ?, ?)",
                (source.source_id, canonical_url, source.model_dump_json(), now),
            )
            connection.execute(
                "INSERT OR REPLACE INTO investigation_sources VALUES (?, ?, ?, ?, ?)",
                (
                    investigation_id,
                    source.source_id,
                    relevance_score,
                    int(relevant),
                    json.dumps(reasons),
                ),
            )

    async def save_many(self, observations: list[Observation]) -> list[Observation]:
        self.observations.update({item.observation_id: item for item in observations})
        with self._connect() as connection:
            connection.executemany(
                "INSERT OR REPLACE INTO observations VALUES (?, ?, ?, datetime('now'))",
                [
                    (item.observation_id, item.source_id, item.model_dump_json())
                    for item in observations
                ],
            )
        return observations

    async def save_investigation_observations(
        self, investigation_id: str, observations: list[Observation]
    ) -> None:
        unique_observations = list({item.observation_id: item for item in observations}.values())
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM investigation_observations WHERE investigation_id = ?",
                (investigation_id,),
            )
            connection.executemany(
                "INSERT INTO investigation_observations VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                [
                    (investigation_id, item.observation_id, item.model_dump_json())
                    for item in unique_observations
                ],
            )

    def get_investigation_clues(self, investigation_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT clues_json FROM investigations WHERE investigation_id = ?",
                (investigation_id,),
            ).fetchone()
        return json.loads(row[0]) if row else None

    def list_investigations(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT i.investigation_id, i.clues_json, i.created_at,
                       (SELECT COUNT(*) FROM investigation_sources s WHERE s.investigation_id = i.investigation_id) AS source_count
                FROM investigations i
                ORDER BY created_at DESC
                """
            ).fetchall()
        return [
            {
                "investigation_id": row["investigation_id"],
                "clues": json.loads(row["clues_json"]),
                "created_at": row["created_at"],
                "source_count": row["source_count"],
            }
            for row in rows
        ]

    def get_relevant_sources(self, investigation_id: str) -> list[RawSource]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT c.source_json FROM source_cache c JOIN investigation_sources i ON i.source_id = c.source_id WHERE i.investigation_id = ? AND i.is_relevant = 1",
                (investigation_id,),
            ).fetchall()
        return [RawSource.model_validate_json(row[0]) for row in rows]

    def get_run(self, run_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT result_json FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return json.loads(row["result_json"]) if row else None

    def get_sources(self, investigation_id: str) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT c.source_json, i.relevance_score, i.is_relevant, i.relevance_reasons FROM source_cache c JOIN investigation_sources i ON i.source_id = c.source_id WHERE i.investigation_id = ? ORDER BY c.fetched_at",
                (investigation_id,),
            ).fetchall()
        return [
            {
                **json.loads(row["source_json"]),
                "relevance_score": row["relevance_score"],
                "is_relevant": bool(row["is_relevant"]),
                "relevance_reasons": json.loads(row["relevance_reasons"]),
            }
            for row in rows
        ]

    def get_observations(self, investigation_id: str) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT observation_json FROM investigation_observations WHERE investigation_id = ? ORDER BY created_at",
                (investigation_id,),
            ).fetchall()
        return [json.loads(row["observation_json"]) for row in rows]
