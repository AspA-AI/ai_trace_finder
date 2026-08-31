import json
import re

import httpx

from app.evidence_pipeline.normalization.observations import NormalizedObservation
from app.evidence_pipeline.resolution.candidates import ComparisonType
from app.evidence_pipeline.verification.contracts import ProfileReconstruction, SemanticDecision


class ConstrainedSemanticVerifier:
    def __init__(self, api_key: str, model: str, timeout: float = 60.0) -> None:
        self.api_key, self.model, self.timeout = api_key, model, timeout

    async def compare(
        self,
        left: NormalizedObservation,
        right: NormalizedObservation,
        features: dict | None = None,
        comparison_type: ComparisonType = ComparisonType.IDENTITY_LINK,
        left_evidence: list[NormalizedObservation] | None = None,
        right_evidence: list[NormalizedObservation] | None = None,
    ) -> SemanticDecision:
        if comparison_type == ComparisonType.FACT_CONSISTENCY:
            task = (
                "These two observations are already confirmed to be about the same person "
                "(same source). Decide whether the two claims are consistent, in conflict, "
                "or a normal change over time (e.g. sequential jobs, project updates).\n"
                "MATCH: the claims are compatible or complementary.\n"
                "CONFLICT: the claims cannot both be true for one person at the same time, "
                "and nothing in the evidence explains the difference.\n"
                "TEMPORAL: the claims differ but represent a plausible change over time "
                "rather than a contradiction.\n"
                "UNKNOWN: not enough information to decide."
            )
        else:
            task = (
                "These two observations come from different sources and may or may not be "
                "about the same person. Decide whether they support the same identity.\n"
                "MATCH requires explicit identity evidence (a shared identifier, an explicit "
                "cross-link, or an exact matching claim) — not just a shared name, city, or "
                "occupation, which are common to many people.\n"
                "CONFLICT: the evidence indicates these are different people, or the claims "
                "cannot both be true of one person.\n"
                "TEMPORAL: differing claims plausibly explained by time passing.\n"
                "UNKNOWN: not enough information to decide."
            )
        left_payload = [item.model_dump(mode="json") for item in (left_evidence or [left])]
        right_payload = [item.model_dump(mode="json") for item in (right_evidence or [right])]
        prompt = (
            f"{task}\n\n"
            "Compare only the supplied observations and deterministic features. "
            "Do not use outside knowledge. Return JSON with a single field 'decision' "
            "set to MATCH, CONFLICT, TEMPORAL, or UNKNOWN.\n"
            f"A_EVIDENCE: {left_payload}\nB_EVIDENCE: {right_payload}\nFEATURES: {features or {}}"
        )
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "temperature": 0,
                    "messages": [
                        {"role": "system", "content": "Return strict JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
        value = json.loads(response.json()["choices"][0]["message"]["content"]).get(
            "decision", "UNKNOWN"
        )
        try:
            return SemanticDecision(value)
        except ValueError:
            return SemanticDecision.UNKNOWN


class ProfileReconstructionVerifier:
    """Runs a single, independent analysis over every observation collected
    for an investigation. Deliberately does NOT receive Python's per-pair
    features or verdicts — this is meant to be a parallel read of the raw
    evidence, not a review of the deterministic layer's shortlist."""

    def __init__(self, api_key: str, model: str, timeout: float = 90.0) -> None:
        self.api_key, self.model, self.timeout = api_key, model, timeout

    async def analyze(
        self,
        clues: dict,
        observations: list[NormalizedObservation],
        photo_candidates: list[dict] | None = None,
    ) -> ProfileReconstruction:
        prompt = (
            "You are reviewing raw, unverified observations collected from multiple public "
            "sources while investigating a person. The user's original search clues are given "
            "below, along with every observation extracted from every source found.\n\n"
            "Decide, from this evidence alone, whether the observations most likely describe "
            "ONE person or MULTIPLE different people who happen to share the same name or "
            "similar attributes. Do not assume they are the same person just because the name "
            "matches — shared names, cities, and occupations are common. Look for genuine "
            "corroboration (consistent, non-generic details repeating across independent "
            "sources) versus genuine contradiction (mutually exclusive facts, implausible "
            "combinations, or details that only make sense for a different person).\n\n"
            "Target scoping is mandatory: treat every supplied user clue as a filter, not merely "
            "as background. First identify the target described by the complete clue set. "
            "Observations that clearly describe a different occupation, employer, location, "
            "career, or person are out-of-scope name-collision evidence. Exclude them from the "
            "profile's likely_name, headline, attributes, supporting evidence, and main reasoning. "
            "Mention them only in excluded_evidence_summary or caveats as a concise warning that "
            "the same name produced unrelated results. Do not call an out-of-scope occupation a "
            "conflict about the target unless the evidence independently establishes that it is "
            "the same individual.\n\n"
            "Volume and fame are not evidence: never let the identity with the most observations, "
            "the most sources, or the most publicly recognizable career win by default. A user clue "
            "like a specific occupation or employer is a hard filter. If only one or two observations "
            "match that clue while dozens describe a more prominent same-name person in an unrelated "
            "field, the sparse clue-matching evidence is still the target, and the prominent evidence "
            "is the out-of-scope collision — not the other way around. Anchor likely_name, headline, "
            "profile_summary, and attributes on the clue-matching evidence even when it is thin, and "
            "say so plainly if it is too thin to build a confident profile from.\n\n"
            "Evidence standard: strong evidence includes an explicit cross-link, exact stable "
            "username or email, a source-controlled profile URL, or several independent sources "
            "repeating distinctive facts unlikely to belong to another person. Medium evidence "
            "includes a consistent employer, project, education, timeline, or location when "
            "combined across independent sources. Weak evidence includes name-only matches, "
            "generic occupations, common locations, search-result snippets, or similar writing. "
            "Weak evidence alone must never support likely_same_person. If strong corroboration "
            "is missing or sources conflict, choose insufficient_evidence or likely_multiple_people. "
            "Use probability language throughout the profile; never state an unverified fact as certain.\n\n"
            "Return strict JSON with these fields:\n"
            '- "verdict": one of "likely_same_person", "likely_multiple_people", "insufficient_evidence"\n'
            '- "confidence_label": one of "high", "medium", "low"\n'
            '- "likely_name": the best-supported person name, or null if unclear\n'
            '- "headline": a short professional description, or null if unclear\n'
            '- "profile_summary": a professional paragraph describing what this evidence supports; '
            "do not present an unverified identity as fact\n"
            '- "attributes": a list of objects with "field", "value", "confidence_label", '
            '"supporting_observation_ids", and optional "caveat"; include useful fields such as '
            "occupation, location, employers, usernames, websites, education, and work history "
            "only when supported by the observations\n"
            '- "photo_url": always null\n'
            '- "photo_source_observation_id": always null; image review is kept outside the identity profile\n'
            '- "reasoning": a clear explanation a non-technical reviewer could follow, '
            "citing the specific corroborating or conflicting details you weighed\n"
            '- "supporting_observation_ids": observation_ids that support your verdict\n'
            '- "conflicting_observation_ids": observation_ids that work against it, if any\n'
            '- "out_of_scope_observation_ids": observations excluded because they describe a '
            "different same-name person or do not match the user's target clues\n"
            '- "excluded_evidence_summary": a short explanation of excluded same-name or '
            "out-of-scope evidence, or null\n"
            '- "caveats": short list of anything that should make a reviewer double check '
            "your verdict (e.g. missing dates, single-source claims, generic details only)\n\n"
            "Pronouns: use neutral language such as 'the person' or 'they'. Never infer gender "
            "or pronouns from a name, photo, occupation, or writing style. Only mention a "
            "specific pronoun when it is explicitly written in a supplied observation, and cite "
            "that observation.\n\n"
            f"CLUES: {json.dumps(clues)}\n\n"
            f"OBSERVATIONS: {json.dumps([item.model_dump(mode='json') for item in observations])}"
        )
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "temperature": 0,
                    "messages": [
                        {"role": "system", "content": "Return strict JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
        payload = json.loads(response.json()["choices"][0]["message"]["content"])
        # Models can occasionally return null for required narrative fields;
        # normalize that response before contract validation so a malformed
        # optional narrative cannot turn verification into a server error.
        payload["profile_summary"] = payload.get("profile_summary") or ""
        payload["reasoning"] = payload.get("reasoning") or ""
        payload["attributes"] = payload.get("attributes") or []
        payload["caveats"] = payload.get("caveats") or []
        payload["supporting_observation_ids"] = payload.get("supporting_observation_ids") or []
        payload["conflicting_observation_ids"] = payload.get("conflicting_observation_ids") or []
        payload["out_of_scope_observation_ids"] = payload.get("out_of_scope_observation_ids") or []
        profile = ProfileReconstruction.model_validate(payload)
        # Images are never interpreted or selected by the LLM profile track.
        profile.photo_url = None
        profile.photo_source_observation_id = None
        profile = _enforce_target_scope(profile, clues, observations)
        profile = _realign_to_clue_occupation(profile, clues, observations)
        return profile


def _clue_terms(value: str) -> list[str]:
    return [term for term in re.findall(r"[a-z0-9]+", value.lower()) if len(term) > 2]


def _enforce_target_scope(
    profile: ProfileReconstruction,
    clues: dict,
    observations: list[NormalizedObservation],
) -> ProfileReconstruction:
    """Prevent a strong same-name result from replacing the requested target.

    The model may notice a famous or better-documented namesake. That is useful
    collision context, but it is not a working profile when a distinguishing
    user clue has no supporting observation anywhere in the evidence at all.
    """
    searchable = " ".join(
        " ".join(
            str(value or "") for value in (item.predicate, item.original_object, item.quote)
        ).lower()
        for item in observations
    )
    scope_fields = (
        ("occupation", "occupation"),
        ("employers", "employer"),
        ("locations", "location"),
        ("usernames", "username"),
        ("github_handle", "GitHub handle"),
        ("websites", "website"),
    )
    missing = []
    for key, label in scope_fields:
        values = clues.get(key) or []
        if isinstance(values, str):
            values = [values]
        for value in values:
            terms = _clue_terms(str(value))
            if terms and not all(term in searchable for term in terms):
                missing.append((label, str(value)))

    if not missing:
        return profile

    labels = ", ".join(f"{label} '{value}'" for label, value in missing[:3])
    all_ids = [item.observation_id for item in observations]
    return profile.model_copy(
        update={
            "verdict": "insufficient_evidence",
            "confidence_label": "low",
            "likely_name": None,
            "headline": None,
            "profile_summary": (
                f"The captured evidence does not contain support for the requested {labels}. "
                "It may describe other people with the same name, so it is not presented as the target profile."
            ),
            "attributes": [],
            "supporting_observation_ids": [],
            "conflicting_observation_ids": [],
            "out_of_scope_observation_ids": all_ids,
            "excluded_evidence_summary": (
                "Retrieved observations were withheld from the working profile because the supplied "
                "distinguishing clue(s) were not found in the extracted evidence."
            ),
            "reasoning": (
                f"The requested {labels} could not be corroborated by the extracted observations. "
                "The system therefore did not promote a same-name profile that matched different clues."
            ),
            "caveats": [
                "The search may have retrieved a different person with the same name.",
                "Add a location, employer, username, or profile URL to narrow the target.",
            ],
        }
    )


def _realign_to_clue_occupation(
    profile: ProfileReconstruction,
    clues: dict,
    observations: list[NormalizedObservation],
) -> ProfileReconstruction:
    """Catch the case _enforce_target_scope misses: clue-matching evidence
    DOES exist somewhere in the corpus, but the model built its profile
    around a larger, unrelated same-name narrative instead of anchoring on
    the clue. Fame and observation count are not evidence of identity — a
    thin, clue-matching signal should still win over a numerous, non-matching
    one, so re-anchor the profile on the clue-matching evidence directly
    rather than trusting whichever narrative the model happened to favor."""
    occupation_clue = clues.get("occupation")
    if not occupation_clue:
        return profile
    values = [occupation_clue] if isinstance(occupation_clue, str) else list(occupation_clue)
    occupation_terms = [term for value in values for term in _clue_terms(str(value))]
    if not occupation_terms:
        return profile

    def _matches(item: NormalizedObservation) -> bool:
        haystack = f"{item.predicate} {item.original_object or ''} {item.quote or ''}".lower()
        return any(term in haystack for term in occupation_terms)

    matching = [item for item in observations if _matches(item)]
    if not matching:
        return profile  # nothing to anchor on; _enforce_target_scope already handles total absence

    matching_ids = {item.observation_id for item in matching}
    supporting_ids = set(profile.supporting_observation_ids or [])

    # The model's own evidence already includes at least one clue-matching
    # observation — trust that it anchored correctly.
    if supporting_ids & matching_ids:
        return profile

    other_ids = [
        item.observation_id for item in observations if item.observation_id not in matching_ids
    ]
    matched_summary = "; ".join(
        f"{item.predicate}: {item.original_object}" for item in matching[:3]
    )
    clue_display = ", ".join(values)
    return profile.model_copy(
        update={
            "verdict": "insufficient_evidence" if len(matching) <= 1 else "likely_multiple_people",
            "confidence_label": "low",
            "likely_name": None,
            "headline": None,
            "profile_summary": (
                f"The requested occupation ('{clue_display}') is supported only by limited evidence "
                f"({matched_summary}). Most of the retrieved evidence instead describes a different, "
                "more prominent person who shares the same name. That more prominent identity is not "
                "presented as the target because it does not match the occupation specified in the "
                "search input."
            ),
            "attributes": [],
            "supporting_observation_ids": list(matching_ids),
            "conflicting_observation_ids": other_ids,
            "out_of_scope_observation_ids": other_ids,
            "excluded_evidence_summary": (
                "The majority of retrieved observations describe a person with a different, unrelated "
                "occupation than the one specified in the search clues. That evidence was treated as a "
                "likely name collision rather than merged into the target profile."
            ),
            "reasoning": (
                "The evidence contains a large, well-documented narrative about a same-name person in an "
                "unrelated field, alongside only sparse evidence matching the occupation actually "
                "requested. Volume and public prominence are not identity evidence, so the profile was "
                "re-anchored on the sparse clue-matching evidence instead of the larger unrelated "
                "narrative."
            ),
            "caveats": [
                "Only limited evidence matches the requested occupation — treat this result cautiously.",
                "A more prominent, differently-occupied person with the same name was found and excluded.",
                "Add a location, employer, or username to strengthen this search and find more evidence.",
            ],
        }
    )
