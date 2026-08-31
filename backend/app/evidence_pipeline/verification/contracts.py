from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.evidence_pipeline.resolution.candidates import ComparisonType


class VerificationState(StrEnum):
    VERIFIED = "VERIFIED"
    PROBABLE = "PROBABLE"
    UNKNOWN = "UNKNOWN"
    CONTRADICTED = "CONTRADICTED"
    REJECTED = "REJECTED"


class SemanticDecision(StrEnum):
    MATCH = "MATCH"
    CONFLICT = "CONFLICT"
    TEMPORAL = "TEMPORAL"
    UNKNOWN = "UNKNOWN"


class VerificationResult(BaseModel):
    left_observation_id: str
    right_observation_id: str
    comparison_type: ComparisonType
    state: VerificationState
    deterministic_decision: SemanticDecision
    semantic_decision: SemanticDecision | None = None
    confidence_score: float = 0.0
    feature_values: dict[str, bool | int | str | None] = Field(default_factory=dict)
    reason_codes: list[str] = Field(default_factory=list)
    supporting_observation_ids: list[str] = Field(default_factory=list)
    left_evidence_ids: list[str] = Field(default_factory=list)
    right_evidence_ids: list[str] = Field(default_factory=list)
    verifier_version: str = "hybrid-3.1"


class ProfileReconstruction(BaseModel):
    """The LLM's independent, whole-investigation analysis — done in one
    pass over every observation, with no visibility into Python's
    per-pair features or verdicts. This is a separate track, not a
    review of Python's shortlist."""

    verdict: Literal["likely_same_person", "likely_multiple_people", "insufficient_evidence"]
    confidence_label: Literal["high", "medium", "low"]
    likely_name: str | None = None
    headline: str | None = None
    profile_summary: str
    attributes: list["ProfileAttribute"] = Field(default_factory=list)
    # Deliberately never promoted to the working profile. Images are exposed
    # separately as unverified source media for human review.
    photo_url: str | None = None
    photo_source_observation_id: str | None = None
    reasoning: str
    supporting_observation_ids: list[str] = Field(default_factory=list)
    conflicting_observation_ids: list[str] = Field(default_factory=list)
    out_of_scope_observation_ids: list[str] = Field(default_factory=list)
    excluded_evidence_summary: str | None = None
    caveats: list[str] = Field(default_factory=list)


class ProfileAttribute(BaseModel):
    """A user-facing claim in the LLM's working profile, still source-bound."""

    field: str
    value: str | list[str] | None = None
    confidence_label: Literal["high", "medium", "low"]
    supporting_observation_ids: list[str] = Field(default_factory=list)
    caveat: str | None = None


class DualTrackResult(BaseModel):
    investigation_id: str

    # Python's independent analysis, rolled up from per-pair
    # identity_link results into one investigation-level verdict.
    deterministic_verdict: VerificationState
    deterministic_confidence: float
    deterministic_reasoning: list[str] = Field(default_factory=list)

    # The LLM's independent analysis, from ProfileReconstruction above.
    semantic_verdict: str
    semantic_confidence: str
    semantic_reasoning: str
    semantic_caveats: list[str] = Field(default_factory=list)
    semantic_profile: ProfileReconstruction
    image_candidates: list[dict[str, str]] = Field(default_factory=list)

    # Informational only — not a forced merge into one number.
    agreement: Literal["aligned", "diverging", "one_abstained"]
    suggested_action: str | None = None

    generated_at: str
