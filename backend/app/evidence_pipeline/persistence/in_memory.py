from app.evidence_pipeline.contracts.evidence import Observation, RawSource


class InMemoryEvidenceRepository:
    """Development repository; replace with PostgreSQL without changing callers."""

    def __init__(self) -> None:
        self.sources: dict[str, RawSource] = {}
        self.observations: dict[str, Observation] = {}
        self.links: dict[tuple[str, str], dict] = {}

    async def get_cached(self, canonical_url: str, max_age_hours: int):
        return next((item for item in self.sources.values() if str(item.canonical_url or item.url) == canonical_url), None)

    async def link_source(self, investigation_id: str, source: RawSource, relevance_score: float, relevant: bool, reasons: list[str]) -> None:
        self.links[(investigation_id, source.source_id)] = {"score": relevance_score, "relevant": relevant, "reasons": reasons}

    async def save(self, source: RawSource) -> RawSource:
        self.sources[source.source_id] = source
        return source

    async def save_many(self, observations: list[Observation]) -> list[Observation]:
        for observation in observations:
            self.observations[observation.observation_id] = observation
        return observations

    def get_sources(self, investigation_id: str) -> list[dict]:
        return [item.model_dump(mode="json") for item in self.sources.values() if item.investigation_id == investigation_id]

    def get_observations(self, investigation_id: str) -> list[dict]:
        source_ids = {item.source_id for item in self.sources.values() if item.investigation_id == investigation_id}
        return [item.model_dump(mode="json") for item in self.observations.values() if item.source_id in source_ids]
