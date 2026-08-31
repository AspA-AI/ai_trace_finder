from urllib.parse import urlsplit

from app.evidence_pipeline.normalization.observations import NormalizedObservation
from app.evidence_pipeline.resolution.candidates import CandidatePair
from app.evidence_pipeline.verification.contracts import (
    SemanticDecision,
    VerificationResult,
    VerificationState,
)

# Predicates that can only hold one true value for a person at a given time.
SINGLE_VALUED_PREDICATES = {
    "location",
    "current_location",
    "occupation",
    "email",
    "date_of_birth",
}

# Predicates that are naturally repeatable — a person can have many.
MULTI_VALUED_PREDICATES = {
    "experience",
    "developedtool",
    "project",
    "engineered",
    "used",
    "passed",
    "compiled",
    "benchmarked",
    "achieved",
    "ensures",
    "has_created",
    "is_involved_in",
}

# --- Source Authority Matrix -------------------------------------------
# Illustrative starting weights per source_platform. These are placeholders
# — tune against real cases (WHOIS/registry-verified sources should sit
# near 1.0, unverified forum posts near the bottom) once you have a
# ground-truth set to calibrate against.
SOURCE_AUTHORITY_WEIGHTS: dict[str, float] = {
    "github": 0.9,
    "linkedin": 0.7,
    "ultralytics": 0.5,
    "twine": 0.4,
}
DEFAULT_SOURCE_AUTHORITY_WEIGHT = 0.3

# --- Confidence formula ---------------------------------------------------
# Confidence = w1*LinkOverlap + w2*SourceWeight - w3*ConflictPenalty
# All three terms are normalized to [0, 1] before weighting.
LINK_OVERLAP_WEIGHTS: dict[str, float] = {
    "explicit_crosslink": 0.40,
    "same_identifier": 0.35,
    "matching_source_identifier": 0.35,
    "same_claim": 0.25,
    "cross_platform_identifier_similarity": 0.15,
    "same_normalized_object": 0.10,
    "same_normalized_subject": 0.05,
}
CONFLICT_PENALTY_CONFIRMED = 1.0  # single-valued contradiction, confirmed overlap
CONFLICT_PENALTY_UNRESOLVED = 0.4  # ambiguous cardinality / unverified temporal order

W_LINK_OVERLAP = 0.5
W_SOURCE_WEIGHT = 0.2
W_CONFLICT_PENALTY = 0.3


def _predicate_key(predicate: str) -> str:
    return predicate.lower().replace(" ", "_")


def _cardinality(predicate: str) -> str:
    key = _predicate_key(predicate)
    if key in SINGLE_VALUED_PREDICATES:
        return "single"
    if key in MULTI_VALUED_PREDICATES:
        return "multi"
    return "unknown"


def _is_identifier(predicate: str) -> bool:
    value = _predicate_key(predicate)
    return any(
        token in value for token in ("username", "handle", "github", "profile_id", "identifier")
    )


def _domain(url: str) -> str:
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def _matching_identifier(left: NormalizedObservation, right: NormalizedObservation) -> bool:
    return any(
        a == b and left.source_platform == right.source_platform
        for a in left.source_identifiers
        for b in right.source_identifiers
    )


def _cross_platform_identifier_similarity(
    left: NormalizedObservation, right: NormalizedObservation
) -> bool:
    return any(
        a == b and left.source_platform != right.source_platform
        for a in left.source_identifiers
        for b in right.source_identifiers
    )


def _validity_overlaps(left: NormalizedObservation, right: NormalizedObservation) -> bool | None:
    """True/False if we can tell whether the two claims' time windows
    overlap. None means we don't have enough date data to say either way —
    callers must not assume 'no overlap' in that case."""
    if left.valid_from is None or right.valid_from is None:
        return None
    left_end = left.valid_until or "9999-12-31"
    right_end = right.valid_until or "9999-12-31"
    return left.valid_from <= right_end and right.valid_from <= left_end


def _source_weight(observation: NormalizedObservation) -> float:
    return SOURCE_AUTHORITY_WEIGHTS.get(
        observation.source_platform, DEFAULT_SOURCE_AUTHORITY_WEIGHT
    )


def _link_overlap(feature_values: dict) -> float:
    score = sum(weight for key, weight in LINK_OVERLAP_WEIGHTS.items() if feature_values.get(key))
    return min(score, 1.0)


def _source_weight_for_pair(
    left_group: list[NormalizedObservation], right_group: list[NormalizedObservation]
) -> float:
    left_weight = max(
        (_source_weight(item) for item in left_group), default=DEFAULT_SOURCE_AUTHORITY_WEIGHT
    )
    right_weight = max(
        (_source_weight(item) for item in right_group), default=DEFAULT_SOURCE_AUTHORITY_WEIGHT
    )
    return (left_weight + right_weight) / 2


def _confidence_score(
    feature_values: dict,
    left_group: list[NormalizedObservation],
    right_group: list[NormalizedObservation],
    conflict_penalty: float,
) -> float:
    link_overlap = _link_overlap(feature_values)
    source_weight = _source_weight_for_pair(left_group, right_group)
    score = (
        W_LINK_OVERLAP * link_overlap
        + W_SOURCE_WEIGHT * source_weight
        - W_CONFLICT_PENALTY * conflict_penalty
    )
    return round(max(0.0, min(1.0, score)), 3)


def verify_candidate(
    pair: CandidatePair, observations: dict[str, NormalizedObservation]
) -> VerificationResult:
    left = observations[pair.left_observation_id]
    right = observations[pair.right_observation_id]

    left_group = [
        observations[item] for item in pair.left_evidence_ids if item in observations
    ] or [left]
    right_group = [
        observations[item] for item in pair.right_evidence_ids if item in observations
    ] or [right]

    same_subject = any(
        a.normalized_subject and a.normalized_subject == b.normalized_subject
        for a in left_group
        for b in right_group
    )
    same_object = any(
        a.normalized_object and a.normalized_object == b.normalized_object
        for a in left_group
        for b in right_group
    )
    same_identifier = any(
        _is_identifier(a.predicate)
        and _is_identifier(b.predicate)
        and a.normalized_object == b.normalized_object
        for a in left_group
        for b in right_group
    )
    matching_source_identifier = any(
        _matching_identifier(a, b) for a in left_group for b in right_group
    )
    cross_platform_identifier_similarity = any(
        _cross_platform_identifier_similarity(a, b) for a in left_group for b in right_group
    )
    same_source_domain = any(
        _domain(a.source_url) == _domain(b.source_url) for a in left_group for b in right_group
    )
    explicit_crosslink = any(
        a.normalized_object == b.source_url or b.normalized_object == a.source_url
        for a in left_group
        for b in right_group
    )
    same_claim = any(
        _predicate_key(a.predicate) == _predicate_key(b.predicate)
        and a.normalized_object
        and a.normalized_object == b.normalized_object
        for a in left_group
        for b in right_group
    )
    conflicting_pairs = [
        (a, b)
        for a in left_group
        for b in right_group
        if _predicate_key(a.predicate) == _predicate_key(b.predicate)
        and a.normalized_object
        and b.normalized_object
        and a.normalized_object != b.normalized_object
    ]
    different_object_same_predicate = bool(conflicting_pairs)

    conflict_left, conflict_right = conflicting_pairs[0] if conflicting_pairs else (left, right)
    same_predicate = _predicate_key(conflict_left.predicate) == _predicate_key(
        conflict_right.predicate
    )
    cardinality = _cardinality(conflict_left.predicate) if same_predicate else "unknown"
    overlap = (
        _validity_overlaps(conflict_left, conflict_right)
        if different_object_same_predicate
        else None
    )

    conflicting_object = False
    needs_temporal_review = False
    reasons = list(pair.reasons)

    if different_object_same_predicate:
        if cardinality == "single":
            if overlap is True:
                conflicting_object = True
                reasons.append("CONFLICTING_SINGLE_VALUED_CLAIM")
            elif overlap is False:
                reasons.append("SEQUENTIAL_VALUE_CHANGE")  # e.g. relocation — not a conflict
            else:
                needs_temporal_review = True
                reasons.append("UNVERIFIED_TEMPORAL_ORDER")
        elif cardinality == "multi":
            reasons.append("MULTIPLE_VALUES_SAME_PREDICATE")
        else:
            needs_temporal_review = True
            reasons.append("UNKNOWN_PREDICATE_CARDINALITY")

    if conflicting_object and pair.comparison_type.value == "fact_consistency":
        decision = SemanticDecision.CONFLICT
        state = VerificationState.CONTRADICTED
    elif needs_temporal_review:
        decision = SemanticDecision.TEMPORAL
        state = VerificationState.UNKNOWN
    else:
        decision = SemanticDecision.UNKNOWN
        state = VerificationState.UNKNOWN

    if same_identifier:
        reasons.append("EXACT_IDENTIFIER_AGREEMENT")
    if matching_source_identifier:
        reasons.append("MATCHING_SOURCE_IDENTIFIER")
    if cross_platform_identifier_similarity:
        reasons.append("CROSS_PLATFORM_IDENTIFIER_SIMILARITY")
    if explicit_crosslink:
        reasons.append("EXPLICIT_CROSSLINK")
    if same_source_domain:
        reasons.append("SAME_SOURCE_DOMAIN")

    feature_values = {
        "same_normalized_subject": same_subject,
        "same_identifier": same_identifier,
        "matching_source_identifier": matching_source_identifier,
        "cross_platform_identifier_similarity": cross_platform_identifier_similarity,
        "same_normalized_object": same_object,
        "same_claim": same_claim,
        "same_source_domain": same_source_domain,
        "explicit_crosslink": explicit_crosslink,
        "different_object_same_predicate": different_object_same_predicate,
        "predicate_cardinality": cardinality,
        "validity_overlap": overlap,
        "conflicting_claim": conflicting_object,
        "different_source": left.source_id != right.source_id,
        "independent_sources": left.source_id != right.source_id
        and left.source_url != right.source_url,
    }

    conflict_penalty = 0.0
    if conflicting_object:
        conflict_penalty = CONFLICT_PENALTY_CONFIRMED
    elif needs_temporal_review:
        conflict_penalty = CONFLICT_PENALTY_UNRESOLVED

    confidence_score = _confidence_score(feature_values, left_group, right_group, conflict_penalty)

    return VerificationResult(
        left_observation_id=left.observation_id,
        right_observation_id=right.observation_id,
        comparison_type=pair.comparison_type,
        state=state,
        deterministic_decision=decision,
        confidence_score=confidence_score,
        feature_values=feature_values,
        reason_codes=sorted(set(reasons or ["INSUFFICIENT_IDENTITY_EVIDENCE"])),
        supporting_observation_ids=[item.observation_id for item in [*left_group, *right_group]],
        left_evidence_ids=[item.observation_id for item in left_group],
        right_evidence_ids=[item.observation_id for item in right_group],
    )


def verify_candidates(
    pairs: list[CandidatePair], observations: list[NormalizedObservation]
) -> list[VerificationResult]:
    indexed = {item.observation_id: item for item in observations}
    return [
        verify_candidate(pair, indexed)
        for pair in pairs
        if pair.left_observation_id in indexed and pair.right_observation_id in indexed
    ]
