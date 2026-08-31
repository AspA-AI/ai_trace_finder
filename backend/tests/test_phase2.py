from app.evidence_pipeline.contracts.evidence import Observation
from app.evidence_pipeline.normalization.observations import normalize_observation
from app.evidence_pipeline.resolution.candidates import generate_candidate_pairs


def test_normalizes_location_aliases() -> None:
    observation = Observation(
        observation_id="o1", source_id="s1", predicate="location", object_text="Wien",
        observed_at="2026-08-23T00:00:00Z", source_url="https://example.com", extraction_model="test", extraction_version="1"
    )
    assert normalize_observation(observation).normalized_object == "vienna"


def test_candidate_generation_only_proposes_cross_source_pairs() -> None:
    left = normalize_observation(Observation(
        observation_id="o1", source_id="s1", subject_text="Jane Doe", predicate="occupation", object_text="Engineer",
        observed_at="2026-08-23T00:00:00Z", source_url="https://a.example", extraction_model="test", extraction_version="1"
    ))
    right = normalize_observation(Observation(
        observation_id="o2", source_id="s2", subject_text="Jane Doe", predicate="occupation", object_text="Engineer",
        observed_at="2026-08-23T00:00:00Z", source_url="https://b.example", extraction_model="test", extraction_version="1"
    ))
    pairs = generate_candidate_pairs([left, right])
    assert pairs[0].reasons == ["same_normalized_object", "same_normalized_subject", "same_predicate_and_object"]
