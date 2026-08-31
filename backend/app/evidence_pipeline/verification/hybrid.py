from app.evidence_pipeline.normalization.observations import NormalizedObservation
from app.evidence_pipeline.resolution.candidates import ComparisonType
from app.evidence_pipeline.verification.contracts import (
    SemanticDecision,
    VerificationResult,
    VerificationState,
)
from app.evidence_pipeline.verification.semantic import ConstrainedSemanticVerifier


def _needs_semantic_review(result: VerificationResult) -> bool:
    """Only spend LLM budget on pairs the deterministic layer could not
    resolve on its own — except identity_link pairs, which now default to
    review. Since candidate generation bundles identity_link comparisons to
    one per source pair (not one per observation pair), there are only a
    handful per investigation, making it cheap to always get a semantic
    read on the question they exist to answer: does this pair of sources
    describe the same person. A bare shared-subject-name pair with no other
    signal is exactly the ambiguous case an LLM read helps most with."""
    features = result.feature_values

    if result.state == VerificationState.CONTRADICTED:
        return True

    if result.comparison_type == ComparisonType.IDENTITY_LINK:
        if bool(features.get("explicit_crosslink")):
            # Deterministically resolved to VERIFIED already; no need to spend budget.
            return False
        return True

    if "UNVERIFIED_TEMPORAL_ORDER" in result.reason_codes:
        return True
    if "UNKNOWN_PREDICATE_CARDINALITY" in result.reason_codes:
        return True
    if "MULTIPLE_VALUES_SAME_PREDICATE" in result.reason_codes:
        return True
    if (
        features.get("same_claim")
        or features.get("explicit_crosslink")
        or features.get("same_identifier")
        or features.get("matching_source_identifier")
    ):
        return True
    return False


def _priority(result: VerificationResult) -> int:
    """Lower number = reviewed first when the semantic budget is limited."""
    if result.state == VerificationState.CONTRADICTED:
        return 0
    if result.comparison_type == ComparisonType.IDENTITY_LINK:
        # Few of these exist per investigation (source-level bundling), and
        # they answer the highest-stakes question (same person or not) —
        # review them right after confirmed contradictions.
        return 1
    if (
        "UNKNOWN_PREDICATE_CARDINALITY" in result.reason_codes
        or "UNVERIFIED_TEMPORAL_ORDER" in result.reason_codes
    ):
        return 2
    if (
        result.feature_values.get("explicit_crosslink")
        or result.feature_values.get("same_identifier")
        or result.feature_values.get("matching_source_identifier")
    ):
        return 3
    if "MULTIPLE_VALUES_SAME_PREDICATE" in result.reason_codes:
        return 4
    if result.feature_values.get("same_claim"):
        return 5
    return 6


def _policy(result: VerificationResult, semantic: SemanticDecision | None) -> VerificationState:
    features = result.feature_values

    if result.comparison_type == ComparisonType.FACT_CONSISTENCY:
        if semantic == SemanticDecision.CONFLICT:
            return VerificationState.CONTRADICTED
        if semantic == SemanticDecision.TEMPORAL:
            return VerificationState.UNKNOWN
        if result.state == VerificationState.CONTRADICTED and semantic in (
            None,
            SemanticDecision.MATCH,
        ):
            return VerificationState.CONTRADICTED
        return VerificationState.UNKNOWN

    # IDENTITY_LINK pairs (cross-source): deciding whether two sources
    # describe the same person.
    if result.state == VerificationState.CONTRADICTED:
        return VerificationState.CONTRADICTED
    if bool(features.get("explicit_crosslink")):
        return VerificationState.VERIFIED
    if semantic == SemanticDecision.CONFLICT:
        return VerificationState.CONTRADICTED
    # A shared employer/project/location claim is not identity-specific.
    # Only exact identifiers accepted by the source semantics may support a
    # PROBABLE identity result; explicit cross-links are handled above.
    strong = int(bool(features.get("same_identifier"))) + int(
        bool(features.get("matching_source_identifier"))
    )
    if semantic == SemanticDecision.MATCH and strong >= 1:
        return VerificationState.PROBABLE
    if semantic == SemanticDecision.MATCH:
        # No hard anchor, but the LLM still read it as a plausible match —
        # keep it UNKNOWN rather than silently promoting, but this is where
        # a human reviewer's own context is most valuable.
        return VerificationState.UNKNOWN
    return VerificationState.UNKNOWN


def _adjust_confidence(base_confidence: float, semantic: SemanticDecision | None) -> float:
    """The deterministic confidence score is computed before the semantic
    verifier runs. Once we have its opinion, nudge the score to reflect it,
    without letting the LLM alone drive confidence to the extremes."""
    if semantic == SemanticDecision.CONFLICT:
        return round(min(base_confidence, 0.05), 3)
    if semantic == SemanticDecision.MATCH:
        return round(min(1.0, base_confidence + 0.2), 3)
    if semantic == SemanticDecision.TEMPORAL:
        return round(max(0.0, base_confidence - 0.05), 3)
    return base_confidence


async def verify_hybrid(
    results: list[VerificationResult],
    observations: list[NormalizedObservation],
    verifier: ConstrainedSemanticVerifier | None,
    max_comparisons: int = 10,
) -> list[VerificationResult]:
    indexed = {item.observation_id: item for item in observations}
    ordered = sorted(range(len(results)), key=lambda i: _priority(results[i]))

    decisions: dict[int, SemanticDecision] = {}
    semantic_count = 0
    if verifier:
        for i in ordered:
            if semantic_count >= max_comparisons:
                break
            result = results[i]
            if not _needs_semantic_review(result):
                continue
            decisions[i] = await verifier.compare(
                indexed[result.left_observation_id],
                indexed[result.right_observation_id],
                result.feature_values,
                comparison_type=result.comparison_type,
                left_evidence=[
                    indexed[item] for item in result.left_evidence_ids if item in indexed
                ],
                right_evidence=[
                    indexed[item] for item in result.right_evidence_ids if item in indexed
                ],
            )
            semantic_count += 1

    enriched = []
    for i, result in enumerate(results):
        decision = decisions.get(i)
        reasons = list(result.reason_codes)
        if decision:
            reasons.append(f"SEMANTIC_{decision.value}")
        enriched.append(
            result.model_copy(
                update={
                    "state": _policy(result, decision),
                    "semantic_decision": decision,
                    "confidence_score": _adjust_confidence(result.confidence_score, decision),
                    "reason_codes": sorted(set(reasons)),
                }
            )
        )
    return enriched


enrich_unknowns = verify_hybrid
