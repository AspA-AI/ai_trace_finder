from datetime import datetime, timezone

from app.evidence_pipeline.normalization.observations import NormalizedObservation
from app.evidence_pipeline.resolution.candidates import ComparisonType
from app.evidence_pipeline.verification.contracts import (
    DualTrackResult,
    ProfileReconstruction,
    VerificationResult,
    VerificationState,
)
from app.evidence_pipeline.verification.semantic import ProfileReconstructionVerifier

# Rank used to pick the "best" deterministic verdict across all
# identity_link pairs for this investigation. CONTRADICTED dominates
# everything else — one confirmed conflict should not be masked by an
# unrelated VERIFIED pair elsewhere in the same investigation.
_STATE_RANK = {
    VerificationState.CONTRADICTED: 4,
    VerificationState.VERIFIED: 3,
    VerificationState.PROBABLE: 2,
    VerificationState.UNKNOWN: 1,
    VerificationState.REJECTED: 0,
}


def _aggregate_deterministic(
    results: list[VerificationResult],
) -> tuple[VerificationState, float, list[str]]:
    """Roll up per-pair identity_link results into one investigation-level
    verdict. Confidence is the max across pairs (the strongest evidence
    found anywhere), except a contradiction overrides everything."""
    identity_results = [
        item for item in results if item.comparison_type == ComparisonType.IDENTITY_LINK
    ]
    if not identity_results:
        return (
            VerificationState.UNKNOWN,
            0.0,
            ["No identity_link comparisons were generated for this investigation."],
        )

    if any(item.state == VerificationState.CONTRADICTED for item in identity_results):
        contradicted = [
            item for item in identity_results if item.state == VerificationState.CONTRADICTED
        ]
        confidence = max(item.confidence_score for item in contradicted)
        reasoning = sorted({code for item in contradicted for code in item.reason_codes})
        return VerificationState.CONTRADICTED, confidence, reasoning

    best = max(identity_results, key=lambda item: (_STATE_RANK[item.state], item.confidence_score))
    confidence = max(item.confidence_score for item in identity_results)
    reasoning = sorted({code for item in identity_results for code in item.reason_codes})
    return best.state, confidence, reasoning


def _agreement(deterministic_verdict: VerificationState, semantic: ProfileReconstruction) -> str:
    deterministic_positive = deterministic_verdict in (
        VerificationState.VERIFIED,
        VerificationState.PROBABLE,
    )
    deterministic_negative = deterministic_verdict == VerificationState.CONTRADICTED
    semantic_positive = semantic.verdict == "likely_same_person"
    semantic_negative = semantic.verdict == "likely_multiple_people"

    if (
        semantic.verdict == "insufficient_evidence"
        or deterministic_verdict == VerificationState.UNKNOWN
    ):
        if not (deterministic_positive or deterministic_negative) and not (
            semantic_positive or semantic_negative
        ):
            return "one_abstained"

    if (deterministic_positive and semantic_positive) or (
        deterministic_negative and semantic_negative
    ):
        return "aligned"
    if (deterministic_positive and semantic_negative) or (
        deterministic_negative and semantic_positive
    ):
        return "diverging"
    return "one_abstained"


def _suggested_action(
    deterministic_verdict: VerificationState, semantic: ProfileReconstruction, agreement: str
) -> str | None:
    if deterministic_verdict == VerificationState.VERIFIED:
        return None
    if agreement == "diverging":
        return (
            "The two independent analyses disagree — review the conflicting observations "
            "directly before trusting either verdict."
        )
    if (
        deterministic_verdict in (VerificationState.UNKNOWN, VerificationState.PROBABLE)
        and semantic.verdict == "likely_same_person"
    ):
        return (
            "No hard identity anchor (matching identifier, explicit cross-link) was found, "
            "even though the independent analysis leans toward one person. Adding a known "
            "GitHub handle, LinkedIn URL, or email to your search clues would let the "
            "deterministic check confirm this directly."
        )
    if semantic.verdict == "insufficient_evidence":
        return "Add more specific clues (a known handle, employer, or location) and re-run to narrow the search."
    return None


async def build_dual_track_result(
    investigation_id: str,
    clues: dict,
    observations: list[NormalizedObservation],
    identity_results: list[VerificationResult],
    profile_verifier: ProfileReconstructionVerifier,
    photo_candidates: list[dict] | None = None,
) -> DualTrackResult:
    deterministic_verdict, deterministic_confidence, deterministic_reasoning = (
        _aggregate_deterministic(identity_results)
    )

    semantic = await profile_verifier.analyze(clues, observations)

    agreement = _agreement(deterministic_verdict, semantic)
    suggested_action = _suggested_action(deterministic_verdict, semantic, agreement)

    return DualTrackResult(
        investigation_id=investigation_id,
        deterministic_verdict=deterministic_verdict,
        deterministic_confidence=deterministic_confidence,
        deterministic_reasoning=deterministic_reasoning,
        semantic_verdict=semantic.verdict,
        semantic_confidence=semantic.confidence_label,
        semantic_reasoning=semantic.reasoning,
        semantic_caveats=semantic.caveats,
        semantic_profile=semantic,
        image_candidates=[
            {key: str(value) for key, value in item.items() if value is not None}
            for item in (photo_candidates or [])
        ],
        agreement=agreement,
        suggested_action=suggested_action,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
