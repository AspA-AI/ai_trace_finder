import re
from dataclasses import dataclass

from app.evidence_pipeline.contracts.inputs import PersonClues

PLACEHOLDERS = {"string", "null", "none", "n/a", "na", "unknown"}


def _real(value: str | None) -> str:
    value = " ".join((value or "").split())
    return "" if value.lower() in PLACEHOLDERS else value


def _identity_variants(value: str) -> set[str]:
    value = _real(value).lower()
    if not value:
        return set()
    compact = re.sub(r"[^a-z0-9]", "", value)
    return {value, value.replace(" ", "-"), value.replace(" ", "_"), compact}


def matches_identity(value: str | None, clues: PersonClues) -> bool:
    text = re.sub(r"[^a-z0-9]", "", (value or "").lower())
    variants = _identity_variants(clues.name or "")
    variants.update(*( _identity_variants(item) for item in [*clues.usernames, clues.github_handle] if _real(item)))
    for variant in variants:
        compact = re.sub(r"[^a-z0-9]", "", variant)
        if len(compact) < 4 or compact not in text:
            continue
        return True
    return False


@dataclass(frozen=True)
class RelevanceResult:
    score: float
    relevant: bool
    reasons: list[str]


def assess_relevance(clues: PersonClues, *, url: str, title: str | None = None, text: str = "") -> RelevanceResult:
    """Score whether a source is about the investigation target, not just topical."""
    haystack = " ".join([url, title or "", text]).lower()
    reasons: list[str] = []
    score = 0.0

    name_variants = _identity_variants(clues.name or "")
    identity_text = re.sub(r"[^a-z0-9]", "", haystack)
    name_match = bool(name_variants & {name for name in name_variants if name and name in haystack}) or any(
        variant and variant in identity_text for variant in name_variants
    )
    if name_match:
        score += 0.65
        reasons.append("target name found")

    username_variants = [_identity_variants(username) for username in [*clues.usernames, clues.github_handle] if _real(username)]
    username_match = any(
        any(variant in haystack or variant in identity_text for variant in variants)
        for variants in username_variants
        for variant in variants
    )
    for variants in username_variants:
        if any(variant in haystack or variant in identity_text for variant in variants):
            score += 0.65
            reasons.append("target username found")

    clue_terms = [_real(term) for term in [clues.occupation, *clues.employers, *clues.locations]]
    matched_terms = [term for term in clue_terms if term and term.lower() in haystack]
    if matched_terms:
        score += min(0.20, 0.05 * len(matched_terms))
        reasons.append("supplied context found")

    # A named person/handle is the identity anchor. Topic-only matches are not enough.
    has_identity_anchor = bool(name_variants or username_variants)
    identity_match = name_match or username_match
    threshold = 0.60 if has_identity_anchor else 0.20
    return RelevanceResult(
        score=min(score, 1.0),
        relevant=bool(identity_match) and score >= threshold if has_identity_anchor else score >= threshold,
        reasons=reasons,
    )
