import json

import httpx

from app.evidence_pipeline.normalization.observations import NormalizedObservation
from app.business_investigation.contracts import BusinessProfileReconstruction


class OpenAIBusinessProfileVerifier:
    """Independent semantic analysis for businesses.

    This intentionally receives clues and the complete normalized evidence set,
    but never deterministic features, candidate pairs, or deterministic verdicts.
    """

    def __init__(self, api_key: str, model: str, timeout: float = 90.0) -> None:
        self.api_key, self.model, self.timeout = api_key, model, timeout

    async def analyze(
        self, clues: dict, observations: list[NormalizedObservation]
    ) -> BusinessProfileReconstruction:
        prompt = (
            "You are independently reviewing raw, source-grounded observations about a "
            "business or organization. Decide whether the supplied observations describe "
            "one business, multiple businesses with similar names, or are insufficient. "
            "Analyze the complete evidence set; do not use outside knowledge and do not "
            "review or imitate a deterministic algorithm.\n\n"
            "Target scoping is mandatory. Treat every supplied company clue as a filter. "
            "A different company with a similar name, different domain, different products, "
            "or incompatible location is out of scope, not evidence about the target. "
            "Volume, popularity, and a recognizable company name are not evidence.\n\n"
            "Evidence standard: strong evidence includes an official domain, a source-controlled "
            "company profile, an exact repository or domain relationship, an explicit cross-link, "
            "or several independent sources repeating distinctive products, founders, executives, "
            "or company history. Medium evidence includes consistent industry, location, product, "
            "or timeline claims across independent sources. Weak evidence includes name-only, "
            "generic industry, common location, copied text, or a search snippet. Weak evidence "
            "alone must never support likely_same_business. If there is no strong anchor, remain "
            "insufficient_evidence even when the profile sounds plausible.\n\n"
            "Use cautious probability language. Never present an unsupported company fact as "
            "certain. Cite observation IDs for every useful attribute and explain which evidence "
            "was included or excluded. Do not infer legal status, ownership, revenue, or other "
            "high-stakes facts unless explicitly stated in an observation.\n\n"
            "Return strict JSON with exactly these fields:\n"
            '- verdict: "likely_same_business", "likely_multiple_businesses", or "insufficient_evidence"\n'
            '- confidence_label: "high", "medium", or "low"\n'
            "- likely_name, headline, profile_summary\n"
            "- attributes: objects with field, value, confidence_label, supporting_observation_ids, caveat\n"
            "- reasoning: a clear paragraph for a non-technical reviewer\n"
            "- supporting_observation_ids, conflicting_observation_ids, out_of_scope_observation_ids\n"
            "- excluded_evidence_summary: string or null\n"
            "- caveats: list of review warnings\n\n"
            f"CLUES: {json.dumps(clues)}\n\n"
            f"OBSERVATIONS: {json.dumps([item.model_dump(mode='json') for item in observations])}"
        )
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "temperature": 0,
                    "messages": [
                        {"role": "system", "content": "Return strict JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
        payload = json.loads(response.json()["choices"][0]["message"]["content"])
        for key in (
            "profile_summary", "reasoning", "attributes", "caveats",
            "supporting_observation_ids", "conflicting_observation_ids",
            "out_of_scope_observation_ids",
        ):
            payload[key] = payload.get(key) or ([] if key.endswith("ids") or key in {"attributes", "caveats"} else "")
        return BusinessProfileReconstruction.model_validate(payload)
