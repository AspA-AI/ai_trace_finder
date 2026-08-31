import unittest
from unittest.mock import patch

import httpx

from app.core.config import Settings, get_settings
from app.evidence_pipeline.contracts.evidence import Observation
from app.main import app


class FakeRepository:
    def __init__(self, observations: list[Observation], verification: dict | None = None):
        self._observations = observations
        self._verification = verification
        self.saved: dict[str, dict] = {}
        self.profile: dict | None = None

    def get_investigation_clues(self, investigation_id: str) -> dict | None:
        return {"name": "Jane Doe"}

    def get_relevant_sources(self, investigation_id: str) -> list:
        return []

    def get_observations(self, investigation_id: str) -> list[dict]:
        return [item.model_dump(mode="json") for item in self._observations]

    async def save_verification(self, investigation_id: str, run_id: str, result: dict) -> None:
        self.saved[run_id] = result

    def get_verification(self, investigation_id: str, run_id: str | None = None) -> dict | None:
        return self._verification

    async def save_profile(self, investigation_id: str, profile: dict) -> None:
        self.profile = profile


def observation(
    observation_id: str,
    source_id: str,
    source_url: str,
    predicate: str,
    object_text: str,
    *,
    subject: str = "Jane Doe",
    valid_from: str | None = None,
    valid_until: str | None = None,
) -> Observation:
    return Observation(
        observation_id=observation_id,
        source_id=source_id,
        subject_text=subject,
        predicate=predicate,
        object_text=object_text,
        observed_at="2026-08-23T00:00:00Z",
        valid_from=valid_from,
        valid_until=valid_until,
        source_url=source_url,
        extraction_model="test",
        extraction_version="test-1",
    )


async def call_endpoint(repository: FakeRepository) -> dict:
    settings = Settings(database_url="sqlite:///:memory:", openai_api_key=None)
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        with patch("app.api.verification._repository_for", return_value=repository):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post("/investigations/test-investigation/verification")
        assert response.status_code == 200, response.text
        return response.json()
    finally:
        app.dependency_overrides.clear()


async def call_profile_endpoint(repository: FakeRepository) -> dict:
    settings = Settings(database_url="sqlite:///:memory:", openai_api_key=None)
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        with patch("app.api.reporting._repository_for", return_value=repository):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post("/investigations/test-investigation/profile")
        assert response.status_code == 200, response.text
        return response.json()
    finally:
        app.dependency_overrides.clear()


class VerificationEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_same_name_collision_stays_unknown(self) -> None:
        repo = FakeRepository([
            observation("a", "source-a", "https://one.example/jane", "occupation", "Engineer"),
            observation("b", "source-b", "https://two.example/jane", "location", "Vienna"),
        ])
        result = await call_endpoint(repo)
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["results"][0]["state"], "UNKNOWN")

    async def test_cross_platform_slug_similarity_is_not_verified(self) -> None:
        repo = FakeRepository([
            observation("a", "source-a", "https://platform.ultralytics.com/jane-doe", "project", "Vision model"),
            observation("b", "source-b", "https://www.linkedin.com/posts/jane-doe-123abc_project-activity", "project", "Vision model"),
        ])
        result = await call_endpoint(repo)
        item = result["results"][0]
        self.assertIn("cross_platform_identifier_similarity", item["reason_codes"])
        self.assertEqual(item["state"], "UNKNOWN")

    async def test_explicit_crosslink_can_be_verified(self) -> None:
        linked_url = "https://profile.example/jane-doe"
        repo = FakeRepository([
            observation("a", "source-a", "https://one.example/jane", "website", linked_url),
            observation("b", "source-b", linked_url, "occupation", "Engineer"),
        ])
        result = await call_endpoint(repo)
        self.assertEqual(result["results"][0]["state"], "VERIFIED")

    async def test_sequential_location_change_is_not_contradiction(self) -> None:
        repo = FakeRepository([
            observation("a", "source-a", "https://one.example/jane", "location", "Vienna", valid_from="2020-01-01", valid_until="2022-12-31"),
            observation("b", "source-a", "https://one.example/jane", "location", "Berlin", valid_from="2023-01-01"),
        ])
        result = await call_endpoint(repo)
        item = result["results"][0]
        self.assertIn("SEQUENTIAL_VALUE_CHANGE", item["reason_codes"])
        self.assertEqual(item["state"], "UNKNOWN")

    async def test_overlapping_single_valued_claims_are_contradicted(self) -> None:
        repo = FakeRepository([
            observation("a", "source-a", "https://one.example/jane", "location", "Vienna", valid_from="2020-01-01", valid_until="2024-12-31"),
            observation("b", "source-a", "https://one.example/jane", "location", "Berlin", valid_from="2023-01-01"),
        ])
        result = await call_endpoint(repo)
        self.assertEqual(result["results"][0]["state"], "CONTRADICTED")

    async def test_profile_synthesis_merges_only_verified_source_links(self) -> None:
        left = observation("a", "source-a", "https://one.example/jane", "website", "https://two.example/jane")
        right = observation("b", "source-b", "https://two.example/jane", "occupation", "Engineer")
        verification = {
            "results": [{
                "left_observation_id": "a",
                "right_observation_id": "b",
                "comparison_type": "identity_link",
                "state": "VERIFIED",
            }]
        }
        result = await call_profile_endpoint(FakeRepository([left, right], verification))
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["profile"]["source_ids"], ["source-a", "source-b"])

    async def test_profile_synthesis_keeps_ambiguous_sources_separate(self) -> None:
        left = observation("a", "source-a", "https://one.example/jane", "occupation", "Engineer")
        right = observation("b", "source-b", "https://two.example/jane", "occupation", "Musician")
        verification = {
            "results": [{
                "left_observation_id": "a",
                "right_observation_id": "b",
                "comparison_type": "identity_link",
                "state": "UNKNOWN",
            }]
        }
        result = await call_profile_endpoint(FakeRepository([left, right], verification))
        self.assertEqual(result["status"], "unresolved")
        self.assertIsNone(result["profile"])
        self.assertEqual(len(result["candidate_profiles"]), 2)


if __name__ == "__main__":
    unittest.main()
