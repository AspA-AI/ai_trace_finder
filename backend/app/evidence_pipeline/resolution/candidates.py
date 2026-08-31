from enum import StrEnum
from itertools import combinations

from pydantic import BaseModel, Field

from app.evidence_pipeline.normalization.observations import NormalizedObservation


class ComparisonType(StrEnum):
    IDENTITY_LINK = "identity_link"  # cross-source: is this the same underlying person?
    FACT_CONSISTENCY = "fact_consistency"  # same-source: do these claims agree with each other?


class CandidatePair(BaseModel):
    left_observation_id: str
    right_observation_id: str
    comparison_type: ComparisonType = ComparisonType.IDENTITY_LINK
    reasons: list[str] = Field(default_factory=list)
    left_source_id: str | None = None
    right_source_id: str | None = None
    left_evidence_ids: list[str] = Field(default_factory=list)
    right_evidence_ids: list[str] = Field(default_factory=list)


def generate_candidate_pairs(observations: list[NormalizedObservation]) -> list[CandidatePair]:
    pairs: list[CandidatePair] = []
    by_source: dict[str, list[NormalizedObservation]] = {}
    for item in observations:
        by_source.setdefault(item.source_id, []).append(item)

    # Consistency checks remain claim-level, but only compare claims with the
    # same predicate. Comparing every claim on a source creates noise.
    for group in by_source.values():
        for left, right in combinations(group, 2):
            if left.predicate != right.predicate:
                continue
            same_object = bool(left.normalized_object and left.normalized_object == right.normalized_object)
            pairs.append(CandidatePair(
                left_observation_id=left.observation_id,
                right_observation_id=right.observation_id,
                comparison_type=ComparisonType.FACT_CONSISTENCY,
                reasons=["same_source", "same_predicate_and_object" if same_object else "same_predicate_different_object"],
                left_source_id=left.source_id,
                right_source_id=right.source_id,
                left_evidence_ids=[left.observation_id],
                right_evidence_ids=[right.observation_id],
            ))

    # Identity links are source/profile-level comparisons. Produce one pair
    # per source pair instead of a Cartesian product of all claims.
    source_groups = list(by_source.values())
    for left_group, right_group in combinations(source_groups, 2):
        reasons: set[str] = set()
        if any(a.normalized_subject and a.normalized_subject == b.normalized_subject for a in left_group for b in right_group):
            reasons.add("same_normalized_subject")
        if any(a.normalized_object and a.normalized_object == b.normalized_object and a.predicate == b.predicate for a in left_group for b in right_group):
            reasons.update({"same_normalized_object", "same_predicate_and_object"})
        if any(a.normalized_object and a.normalized_object == b.source_url or b.normalized_object and b.normalized_object == a.source_url for a in left_group for b in right_group):
            reasons.add("explicit_crosslink")
        if any(_matching_identifier(a, b) for a in left_group for b in right_group):
            reasons.add("matching_source_identifier")
        if any(_similar_identifier(a, b) for a in left_group for b in right_group):
            reasons.add("cross_platform_identifier_similarity")
        if not reasons:
            continue
        left_anchor, right_anchor = left_group[0], right_group[0]
        pairs.append(CandidatePair(
            left_observation_id=left_anchor.observation_id,
            right_observation_id=right_anchor.observation_id,
            comparison_type=ComparisonType.IDENTITY_LINK,
            reasons=sorted(reasons),
            left_source_id=left_anchor.source_id,
            right_source_id=right_anchor.source_id,
            left_evidence_ids=[item.observation_id for item in left_group],
            right_evidence_ids=[item.observation_id for item in right_group],
        ))
    return pairs


def _matching_identifier(left: NormalizedObservation, right: NormalizedObservation) -> bool:
    return any(
        a == b and left.source_platform == right.source_platform
        for a in left.source_identifiers for b in right.source_identifiers
    )


def _similar_identifier(left: NormalizedObservation, right: NormalizedObservation) -> bool:
    return any(
        a == b and left.source_platform != right.source_platform
        for a in left.source_identifiers for b in right.source_identifiers
    )
