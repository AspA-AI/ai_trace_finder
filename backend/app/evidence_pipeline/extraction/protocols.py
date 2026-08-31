from typing import Protocol

from app.evidence_pipeline.contracts.evidence import Observation, RawSource
from app.evidence_pipeline.contracts.inputs import PersonClues


class ObservationExtractor(Protocol):
    name: str
    version: str

    async def extract(self, source: RawSource, clues: PersonClues) -> list[Observation]: ...
