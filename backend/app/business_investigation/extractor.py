import json
from datetime import datetime, timezone
from hashlib import sha256

import httpx

from app.business_investigation.contracts import BusinessClues
from app.evidence_pipeline.contracts.evidence import Observation, RawSource


class OpenAIBusinessExtractor:
    name = "openai_business_observation_extractor"
    version = "1.0"

    def __init__(self, api_key: str, model: str, timeout: float = 60.0) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def extract(self, source: RawSource, clues: BusinessClues) -> list[Observation]:
        prompt = (
            "Extract only explicit, source-supported observations about the target business. "
            "Do not infer ownership, financial health, legal status, or relationships. "
            "Return JSON with an observations array. Each item must contain predicate, "
            "subject_text, object_text, object_type, and quote. Use null when unknown. "
            "Do not extract unrelated companies or people unless the quote explicitly "
            "relates them to the target business.\n\n"
            f"TARGET BUSINESS CLUES: {clues.model_dump_json()}\n"
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
                        {"role": "system", "content": "You extract business evidence into strict JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            payload = response.json()
        parsed = json.loads(payload["choices"][0]["message"]["content"])
        now = datetime.now(timezone.utc)
        return [
            Observation(
                observation_id=f"obs_{sha256((source.source_id + ':' + str(item.get('quote'))).encode()).hexdigest()[:16]}",
                source_id=source.source_id,
                subject_text=item.get("subject_text"),
                predicate=item.get("predicate", "unknown"),
                object_text=item.get("object_text"),
                object_type=item.get("object_type"),
                observed_at=now,
                quote=item.get("quote"),
                source_url=source.url,
                extraction_model=self.model,
                extraction_version=self.version,
            )
            for item in (parsed if isinstance(parsed, list) else parsed.get("observations", []))
            if item.get("quote")
        ]
