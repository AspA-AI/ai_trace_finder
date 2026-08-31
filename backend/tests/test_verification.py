from app.evidence_pipeline.contracts.evidence import Observation
from app.evidence_pipeline.normalization.observations import normalize_observation
from app.evidence_pipeline.resolution.candidates import CandidatePair, ComparisonType
from app.evidence_pipeline.verification.contracts import VerificationState
from app.evidence_pipeline.verification.deterministic import verify_candidates


def _observation(observation_id: str, source_id: str, location: str) -> Observation:
    return Observation(
        observation_id=observation_id,
        source_id=source_id,
        subject_text="Jane Doe",
        predicate="location",
        object_text=location,
        observed_at="2026-08-23T00:00:00Z",
        source_url="https://example.com",
        extraction_model="test",
        extraction_version="1",
    )


def test_deterministic_verifier_detects_conflicting_locations() -> None:
    def make(observation_id: str, source_id: str, location: str) -> Observation:
        return Observation(observation_id=observation_id, source_id=source_id, subject_text="Jane Doe", predicate="location", object_text=location, valid_from="2026-08-01", observed_at="2026-08-23T00:00:00Z", source_url="https://example.com", extraction_model="test", extraction_version="1")

    observations = [normalize_observation(make("o1", "s1", "Vienna")), normalize_observation(make("o2", "s2", "Berlin"))]
    result = verify_candidates([CandidatePair(left_observation_id="o1", right_observation_id="o2", comparison_type=ComparisonType.FACT_CONSISTENCY)], observations)
    assert result[0].state == VerificationState.CONTRADICTED


def test_same_subject_alone_is_not_identity_proof() -> None:
    left = normalize_observation(_observation("o1", "s1", "Vienna"))
    right = normalize_observation(Observation(
        observation_id="o2", source_id="s2", subject_text="Jane Doe", predicate="occupation", object_text="Engineer",
        observed_at="2026-08-23T00:00:00Z", source_url="https://example.org", extraction_model="test", extraction_version="1"
    ))
    assert verify_candidates([CandidatePair(left_observation_id="o1", right_observation_id="o2")], [left, normalize_observation(right)])[0].state == VerificationState.UNKNOWN
