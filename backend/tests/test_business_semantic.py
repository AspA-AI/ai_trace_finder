from app.business_investigation.semantic import OpenAIBusinessProfileVerifier
from app.evidence_pipeline.normalization.observations import NormalizedObservation


class _Response:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "choices": [
                {
                    "message": {
                        "content": '{"verdict":"likely_same_business","confidence_label":"medium",'
                        '"likely_name":"Acme Robotics","headline":"Robotics company",'
                        '"profile_summary":"The evidence probably describes one robotics business.",'
                        '"attributes":[{"field":"industry","value":"robotics","confidence_label":"high",'
                        '"supporting_observation_ids":["obs-1"]}],"reasoning":"The domain and industry agree.",'
                        '"supporting_observation_ids":["obs-1"],"conflicting_observation_ids":[],'
                        '"out_of_scope_observation_ids":[],"excluded_evidence_summary":null,"caveats":[]}'
                    }
                }
            ]
        }


class _Client:
    last_payload = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, headers, json):
        self.__class__.last_payload = json
        assert url.endswith("/v1/chat/completions")
        return _Response()


async def test_business_semantic_track_reads_complete_evidence(monkeypatch):
    monkeypatch.setattr("app.business_investigation.semantic.httpx.AsyncClient", _Client)
    observation = NormalizedObservation(
        observation_id="obs-1",
        source_id="src-1",
        predicate="industry",
        original_object="robotics",
        normalized_object="robotics",
        source_url="https://acme.example/about",
        source_domain="acme.example",
        source_platform="acme.example",
    )

    result = await OpenAIBusinessProfileVerifier("test-key", "test-model").analyze(
        {"company_name": "Acme Robotics", "industry": "robotics"}, [observation]
    )

    assert result.verdict == "likely_same_business"
    assert result.attributes[0].supporting_observation_ids == ["obs-1"]
    prompt = _Client.last_payload["messages"][1]["content"]
    assert '"company_name": "Acme Robotics"' in prompt
    assert "obs-1" in prompt
    assert "deterministic" not in prompt.lower() or "deterministic algorithm" in prompt.lower()
