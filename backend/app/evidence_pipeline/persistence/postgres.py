import json
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

try:
    import psycopg
except ImportError:  # pragma: no cover - dependency is installed from requirements.txt
    psycopg = None

from app.evidence_pipeline.contracts.evidence import Observation, RawSource


class PostgresEvidenceRepository:
    """PostgreSQL repository for Supabase or any PostgreSQL deployment."""

    def __init__(self, database_url: str) -> None:
        if psycopg is None:
            raise RuntimeError("PostgreSQL support requires psycopg; install requirements.txt")
        self.database_url = self._psycopg_url(database_url)
        self.sources: dict[str, RawSource] = {}
        self.observations: dict[str, Observation] = {}
        self._init_schema()

    @staticmethod
    def _psycopg_url(database_url: str) -> str:
        """Remove Supabase pooler-only query flags unsupported by psycopg."""
        parts = urlsplit(database_url)
        query = [
            (key, value) for key, value in parse_qsl(parts.query) if key.lower() != "pgbouncer"
        ]
        return urlunsplit(
            (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
        )

    def _connect(self):
        # Supabase pooler/PgBouncer can reuse server connections. Disable
        # psycopg auto-prepared statements to avoid statement-name collisions.
        return psycopg.connect(self.database_url, prepare_threshold=None)

    @staticmethod
    def _json_model(value) -> str:
        """Serialize models safely for PostgreSQL JSONB (which rejects NUL)."""
        return (
            json.dumps(value.model_dump(mode="json"), ensure_ascii=False)
            .replace("\x00", "")
            .replace("\\u0000", "")
        )

    def _init_schema(self) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS investigations (
                        investigation_id TEXT PRIMARY KEY,
                        clues_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS runs (
                        run_id TEXT PRIMARY KEY,
                        investigation_id TEXT NOT NULL,
                        result_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS raw_sources (
                        source_id TEXT PRIMARY KEY,
                        investigation_id TEXT NOT NULL,
                        source_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    CREATE TABLE IF NOT EXISTS observations (
                        observation_id TEXT PRIMARY KEY,
                        source_id TEXT NOT NULL,
                        observation_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    CREATE TABLE IF NOT EXISTS investigation_observations (
                        investigation_id TEXT NOT NULL,
                        observation_id TEXT NOT NULL,
                        observation_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        PRIMARY KEY (investigation_id, observation_id)
                    );
                    CREATE TABLE IF NOT EXISTS source_cache (
                        source_id TEXT PRIMARY KEY,
                        canonical_url TEXT UNIQUE NOT NULL,
                        source_json JSONB NOT NULL,
                        fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    CREATE TABLE IF NOT EXISTS investigation_sources (
                        investigation_id TEXT NOT NULL,
                        source_id TEXT NOT NULL,
                        relevance_score DOUBLE PRECISION,
                        is_relevant BOOLEAN NOT NULL,
                        relevance_reasons JSONB NOT NULL,
                        PRIMARY KEY (investigation_id, source_id)
                    );
                    CREATE TABLE IF NOT EXISTS verification_runs (
                        investigation_id TEXT NOT NULL,
                        run_id TEXT NOT NULL,
                        result_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL,
                        PRIMARY KEY (investigation_id, run_id)
                    );
                    CREATE TABLE IF NOT EXISTS profiles (
                        investigation_id TEXT PRIMARY KEY,
                        profile_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL
                    );
                    """
                )
                cursor.execute(
                    "SELECT 1 FROM information_schema.columns WHERE table_name = 'verification_runs' AND column_name = 'run_id'"
                )
                if cursor.fetchone() is None:
                    # Migrate the earlier single-result table in place. The
                    # existing row is retained and receives a stable legacy
                    # run ID so multi-run persistence can be enabled safely.
                    cursor.execute("ALTER TABLE verification_runs ADD COLUMN run_id TEXT")
                    cursor.execute(
                        "UPDATE verification_runs SET run_id = 'legacy_' || md5(investigation_id || created_at::text) WHERE run_id IS NULL"
                    )
                    cursor.execute("ALTER TABLE verification_runs ALTER COLUMN run_id SET NOT NULL")
                    cursor.execute("ALTER TABLE verification_runs DROP CONSTRAINT IF EXISTS verification_runs_pkey")
                    cursor.execute(
                        "ALTER TABLE verification_runs ADD CONSTRAINT verification_runs_pkey PRIMARY KEY (investigation_id, run_id)"
                    )

    async def create_investigation(
        self, investigation_id: str, clues_json: str, created_at: str
    ) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO investigations VALUES (%s, %s::jsonb, %s) ON CONFLICT (investigation_id) DO UPDATE SET clues_json = EXCLUDED.clues_json",
                    (investigation_id, clues_json, created_at),
                )

    async def save_run(
        self, run_id: str, investigation_id: str, result: dict, created_at: str
    ) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO runs VALUES (%s, %s, %s::jsonb, %s) ON CONFLICT (run_id) DO UPDATE SET result_json = EXCLUDED.result_json",
                    (run_id, investigation_id, json.dumps(result), created_at),
                )

    async def save_verification(self, investigation_id: str, run_id: str, result: dict) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO verification_runs (investigation_id, run_id, result_json, created_at) VALUES (%s, %s, %s::jsonb, NOW()) "
                    "ON CONFLICT (investigation_id, run_id) DO UPDATE SET result_json = EXCLUDED.result_json, created_at = NOW()",
                    (investigation_id, run_id, json.dumps(result)),
                )

    def get_verification(self, investigation_id: str, run_id: str | None = None) -> dict | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                if run_id:
                    cursor.execute(
                        "SELECT result_json FROM verification_runs WHERE investigation_id = %s AND run_id = %s",
                        (investigation_id, run_id),
                    )
                else:
                    cursor.execute(
                        "SELECT result_json FROM verification_runs WHERE investigation_id = %s ORDER BY created_at DESC LIMIT 1",
                        (investigation_id,),
                    )
                row = cursor.fetchone()
        return row[0] if row else None

    def list_verification_runs(self, investigation_id: str) -> list[dict]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT run_id, created_at FROM verification_runs WHERE investigation_id = %s ORDER BY created_at DESC",
                    (investigation_id,),
                )
                rows = cursor.fetchall()
        return [{"run_id": row[0], "created_at": row[1].isoformat()} for row in rows]

    async def save_profile(self, investigation_id: str, profile: dict) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO profiles (investigation_id, profile_json, created_at) VALUES (%s, %s::jsonb, NOW()) ON CONFLICT (investigation_id) DO UPDATE SET profile_json = EXCLUDED.profile_json, created_at = NOW()",
                    (investigation_id, json.dumps(profile)),
                )

    def get_profile(self, investigation_id: str) -> dict | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT profile_json FROM profiles WHERE investigation_id = %s", (investigation_id,))
                row = cursor.fetchone()
        return row[0] if row else None

    async def save(self, source: RawSource) -> RawSource:
        self.sources[source.source_id] = source
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO raw_sources (source_id, investigation_id, source_json) VALUES (%s, %s, %s::jsonb) ON CONFLICT (source_id) DO UPDATE SET source_json = EXCLUDED.source_json",
                    (source.source_id, source.investigation_id, self._json_model(source)),
                )
                cursor.execute(
                    "INSERT INTO source_cache (source_id, canonical_url, source_json) VALUES (%s, %s, %s::jsonb) ON CONFLICT (canonical_url) DO UPDATE SET source_id = EXCLUDED.source_id, source_json = EXCLUDED.source_json, fetched_at = NOW()",
                    (
                        source.source_id,
                        str(source.canonical_url or source.url),
                        self._json_model(source),
                    ),
                )
        return source

    async def get_cached(self, canonical_url: str, max_age_hours: int):
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT source_json FROM source_cache WHERE canonical_url = %s AND fetched_at >= %s",
                    (canonical_url, cutoff),
                )
                row = cursor.fetchone()
        return RawSource.model_validate(row[0]) if row else None

    async def link_source(
        self,
        investigation_id: str,
        source: RawSource,
        relevance_score: float,
        relevant: bool,
        reasons: list[str],
    ) -> None:
        canonical_url = str(source.canonical_url or source.url)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO source_cache (source_id, canonical_url, source_json) VALUES (%s, %s, %s::jsonb) ON CONFLICT (canonical_url) DO NOTHING",
                    (source.source_id, canonical_url, self._json_model(source)),
                )
                cursor.execute(
                    "INSERT INTO investigation_sources VALUES (%s, %s, %s, %s, %s::jsonb) ON CONFLICT (investigation_id, source_id) DO UPDATE SET relevance_score = EXCLUDED.relevance_score, is_relevant = EXCLUDED.is_relevant, relevance_reasons = EXCLUDED.relevance_reasons",
                    (
                        investigation_id,
                        source.source_id,
                        relevance_score,
                        relevant,
                        json.dumps(reasons),
                    ),
                )

    async def save_many(self, observations: list[Observation]) -> list[Observation]:
        self.observations.update({item.observation_id: item for item in observations})
        with self._connect() as connection:
            with connection.cursor() as cursor:
                for item in observations:
                    cursor.execute(
                        "INSERT INTO observations (observation_id, source_id, observation_json) VALUES (%s, %s, %s::jsonb) ON CONFLICT (observation_id) DO UPDATE SET observation_json = EXCLUDED.observation_json",
                        (item.observation_id, item.source_id, self._json_model(item)),
                    )
        return observations

    async def save_investigation_observations(
        self, investigation_id: str, observations: list[Observation]
    ) -> None:
        # A source can be discovered through multiple queries. Extraction may
        # therefore return the same deterministic observation ID more than
        # once; collapse the batch before inserting into the composite PK.
        unique_observations = list({item.observation_id: item for item in observations}.values())
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM investigation_observations WHERE investigation_id = %s",
                    (investigation_id,),
                )
                for item in unique_observations:
                    cursor.execute(
                        "INSERT INTO investigation_observations (investigation_id, observation_id, observation_json) VALUES (%s, %s, %s::jsonb) ON CONFLICT (investigation_id, observation_id) DO UPDATE SET observation_json = EXCLUDED.observation_json",
                    (investigation_id, item.observation_id, self._json_model(item)),
                    )

    def get_investigation_clues(self, investigation_id: str) -> dict | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT clues_json FROM investigations WHERE investigation_id = %s",
                    (investigation_id,),
                )
                row = cursor.fetchone()
        return row[0] if row else None

    def list_investigations(self) -> list[dict]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT i.investigation_id, i.clues_json, i.created_at,
                           (SELECT COUNT(*) FROM investigation_sources s WHERE s.investigation_id = i.investigation_id) AS source_count
                    FROM investigations i
                    ORDER BY created_at DESC
                    """
                )
                rows = cursor.fetchall()
        return [
            {
                "investigation_id": row[0],
                "clues": row[1],
                "created_at": row[2].isoformat() if hasattr(row[2], "isoformat") else str(row[2]),
                "source_count": row[3],
            }
            for row in rows
        ]

    def get_relevant_sources(self, investigation_id: str) -> list[RawSource]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT c.source_json FROM source_cache c JOIN investigation_sources i ON i.source_id = c.source_id WHERE i.investigation_id = %s AND i.is_relevant = TRUE",
                    (investigation_id,),
                )
                rows = cursor.fetchall()
                return [RawSource.model_validate(row[0]) for row in rows]

    def get_sources(self, investigation_id: str) -> list[dict]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT c.source_json, i.relevance_score, i.is_relevant, i.relevance_reasons FROM source_cache c JOIN investigation_sources i ON i.source_id = c.source_id WHERE i.investigation_id = %s ORDER BY c.fetched_at",
                    (investigation_id,),
                )
                return [
                    {
                        **row[0],
                        "relevance_score": row[1],
                        "is_relevant": row[2],
                        "relevance_reasons": row[3],
                    }
                    for row in cursor.fetchall()
                ]

    def get_observations(self, investigation_id: str) -> list[dict]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT observation_json FROM investigation_observations WHERE investigation_id = %s ORDER BY created_at",
                    (investigation_id,),
                )
                return [row[0] for row in cursor.fetchall()]
