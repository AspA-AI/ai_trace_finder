import json
from datetime import datetime, timezone
from hashlib import sha256

import httpx

from app.evidence_pipeline.contracts.evidence import Observation, RawSource
from app.evidence_pipeline.contracts.inputs import PersonClues


class OpenAIObservationExtractor:
    name = "openai_observation_extractor"

    def __init__(self, api_key: str, model: str, timeout: float = 60.0) -> None:
        self.api_key = api_key
        self.model = model
        self.version = "1.0"
        self.timeout = timeout

    async def extract(self, source: RawSource, clues: PersonClues) -> list[Observation]:
        prompt = (
            "Extract only explicit, source-supported observations relevant to the target person. "
            "Do not merge identities, infer missing facts, or use outside knowledge. "
            "Return a JSON object with an 'observations' array. Each item has predicate, "
            "subject_text, object_text, object_type, valid_from, valid_until, and quote. "
            "Use null when unknown. "
            "Do not extract facts about unrelated organizations or people unless the quote "
            "explicitly relates them to the target.\n\n"
            f"TARGET CLUES: {clues.model_dump_json()}\n"
            f"SOURCE URL: {source.url}\nSOURCE TEXT:\n{source.content[:50000]}"
        )
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "temperature": 0,
                    "messages": [
                        {"role": "system", "content": "You extract evidence into strict JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            payload = response.json()
        raw_content = payload["choices"][0]["message"]["content"]
        parsed = json.loads(raw_content)
        items = parsed if isinstance(parsed, list) else parsed.get("observations", [])
        now = datetime.now(timezone.utc)
        observations = []
        for item in items:
            quote = item.get("quote")
            if not quote:
                continue
            observations.append(
                Observation(
                    observation_id=f"obs_{sha256(f'{source.source_id}:{quote}'.encode()).hexdigest()[:16]}",
                    source_id=source.source_id,
                    subject_text=item.get("subject_text"),
                    predicate=item.get("predicate", "unknown"),
                    object_text=item.get("object_text"),
                    object_type=item.get("object_type"),
                    observed_at=now,
                    quote=quote,
                    source_url=source.url,
                    extraction_model=self.model,
                    extraction_version=self.version,
                )
            )
        return observations
