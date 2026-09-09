from typing import Literal

from pydantic import BaseModel, Field

from app.evidence_pipeline.verification.contracts import VerificationState


class BusinessClues(BaseModel):
    """Sparse clues for researching a company or business entity."""

    company_name: str
    domains: list[str] = Field(default_factory=list)
    industry: str | None = None
    locations: list[str] = Field(default_factory=list)
    founders: list[str] = Field(default_factory=list)
    executives: list[str] = Field(default_factory=list)
    products: list[str] = Field(default_factory=list)
    known_repositories: list[str] = Field(default_factory=list)
    additional_clues: list[str] = Field(default_factory=list)

    # Compatibility view used only by the shared retrieval service.
    @property
    def name(self) -> str:
        return self.company_name

    @property
    def occupation(self) -> str | None:
        return self.industry

    @property
    def employers(self) -> list[str]:
        return [*self.founders, *self.executives]

    @property
    def websites(self) -> list[str]:
        return self.domains

    @property
    def usernames(self) -> list[str]:
        return self.known_repositories

    @property
    def github_handle(self) -> str | None:
        return None


class BusinessAttribute(BaseModel):
    field: str
    value: str | list[str] | None = None
    confidence_label: Literal["high", "medium", "low"]
    supporting_observation_ids: list[str] = Field(default_factory=list)
    caveat: str | None = None


class BusinessProfileReconstruction(BaseModel):
    """Independent semantic reading of the complete business evidence set."""

    verdict: Literal[
        "likely_same_business",
        "likely_multiple_businesses",
        "insufficient_evidence",
    ]
    confidence_label: Literal["high", "medium", "low"]
    likely_name: str | None = None
    headline: str | None = None
    profile_summary: str
    attributes: list[BusinessAttribute] = Field(default_factory=list)
    reasoning: str
    supporting_observation_ids: list[str] = Field(default_factory=list)
    conflicting_observation_ids: list[str] = Field(default_factory=list)
    out_of_scope_observation_ids: list[str] = Field(default_factory=list)
    excluded_evidence_summary: str | None = None
    caveats: list[str] = Field(default_factory=list)


class BusinessDualTrackResult(BaseModel):
    investigation_id: str
    deterministic_verdict: VerificationState
    deterministic_confidence: float
    deterministic_reasoning: list[str] = Field(default_factory=list)
    semantic_verdict: str
    semantic_confidence: str
    semantic_reasoning: str
    semantic_caveats: list[str] = Field(default_factory=list)
    semantic_profile: BusinessProfileReconstruction
    agreement: Literal["aligned", "diverging", "one_abstained"]
    suggested_action: str | None = None
    generated_at: str
