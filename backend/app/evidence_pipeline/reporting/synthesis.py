from collections import defaultdict

from app.evidence_pipeline.contracts.evidence import Observation


POSITIVE_STATES = {"VERIFIED", "PROBABLE"}


def synthesize_profile(investigation_id: str, observations: list[Observation], verification: dict, investigation_input: dict | None = None) -> dict:
    """Build a profile only from source links accepted by verification.

    Unknown and contradicted links remain visible as unresolved evidence; they
    are never silently merged into the resolved profile.
    """
    by_observation = {item.observation_id: item for item in observations}
    source_by_observation = {item.observation_id: item.source_id for item in observations}
    source_urls: dict[str, set[str]] = defaultdict(set)
    for item in observations:
        source_urls[item.source_id].add(str(item.source_url))

    parent: dict[str, str] = {source_id: source_id for source_id in source_urls}

    def find(source_id: str) -> str:
        while parent[source_id] != source_id:
            parent[source_id] = parent[parent[source_id]]
            source_id = parent[source_id]
        return source_id

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    results = verification.get("results", [])
    for result in results:
        if result.get("comparison_type") != "identity_link" or result.get("state") not in POSITIVE_STATES:
            continue
        left_source = source_by_observation.get(result.get("left_observation_id"))
        right_source = source_by_observation.get(result.get("right_observation_id"))
        if left_source and right_source:
            union(left_source, right_source)

    grouped: dict[str, list[Observation]] = defaultdict(list)
    for item in observations:
        grouped[find(item.source_id)].append(item)

    profiles = []
    for root, items in grouped.items():
        claims: dict[tuple[str, str | None], dict] = {}
        for item in items:
            key = (item.predicate, item.object_text)
            claims.setdefault(key, {
                "predicate": item.predicate,
                "object": item.object_text,
                "object_type": item.object_type,
                "evidence_ids": [],
                "quotes": [],
                "source_urls": [],
            })
            claim = claims[key]
            claim["evidence_ids"].append(item.observation_id)
            if item.quote and item.quote not in claim["quotes"]:
                claim["quotes"].append(item.quote)
            if str(item.source_url) not in claim["source_urls"]:
                claim["source_urls"].append(str(item.source_url))
        profiles.append({
            "candidate_id": f"candidate_{root}",
            "source_ids": sorted({item.source_id for item in items}),
            "source_urls": sorted({url for item in items for url in source_urls[item.source_id]}),
            "observation_count": len(items),
            "claims": list(claims.values()),
            "resolved": len({item.source_id for item in items}) > 1,
        })

    positive_links = [item for item in results if item.get("comparison_type") == "identity_link" and item.get("state") in POSITIVE_STATES]
    unresolved_links = [item for item in results if item.get("comparison_type") == "identity_link" and item.get("state") == "UNKNOWN"]
    contradictions = [item for item in results if item.get("state") == "CONTRADICTED"]
    resolved_profiles = [item for item in profiles if item["resolved"]]
    status = "resolved" if len(resolved_profiles) == 1 else "ambiguous" if len(resolved_profiles) > 1 else "unresolved"
    primary = resolved_profiles[0] if len(resolved_profiles) == 1 else None
    identity_links = [item for item in results if item.get("comparison_type") == "identity_link"]
    state_counts = {state: sum(1 for item in identity_links if item.get("state") == state) for state in ("VERIFIED", "PROBABLE", "UNKNOWN", "CONTRADICTED", "REJECTED")}
    if status == "resolved":
        decision_summary = (
            f"Resolved: {len(primary['source_ids'])} source nodes are connected by "
            f"{len(positive_links)} accepted identity relationship(s)."
        )
        decision_reasons = [
            "At least one VERIFIED or PROBABLE identity relationship connected the source evidence.",
            "The accepted links formed one connected source group rather than multiple competing profiles.",
        ]
    elif status == "ambiguous":
        decision_summary = (
            f"Ambiguous: the evidence formed {len(resolved_profiles)} separate connected source groups, "
            "so the system did not choose one profile."
        )
        decision_reasons = [
            "More than one independently connected source group remained.",
            "Choosing one group would require an unsupported identity assumption.",
        ]
    else:
        decision_summary = (
            "Unresolved: the investigation produced evidence, but no accepted identity relationship "
            "connected enough source nodes to form one profile."
        )
        decision_reasons = [
            "Relevant source content is not the same as proof that two sources describe the same person.",
            "The available comparisons did not provide an identity anchor strong enough to merge sources.",
        ]
    if state_counts["UNKNOWN"]:
        decision_reasons.append(f"{state_counts['UNKNOWN']} identity comparison(s) remained UNKNOWN because the evidence was insufficient.")
    if state_counts["CONTRADICTED"]:
        decision_reasons.append(f"{state_counts['CONTRADICTED']} comparison(s) contained conflicting evidence and were not merged.")
    if not identity_links:
        decision_reasons.append("No identity comparisons were available; the result cannot be resolved from observations alone.")
    input_data = investigation_input or {}
    missing_fields = [
        label for key, label in (
            ("usernames", "a platform username"),
            ("employers", "an employer or organization"),
            ("locations", "a city or country"),
            ("websites", "a known website or profile URL"),
            ("github_handle", "a GitHub handle"),
            ("additional_clues", "another distinguishing clue"),
        ) if not input_data.get(key)
    ]
    next_steps = (
        ["Review the accepted source links before publishing the profile."]
        if status == "resolved" else
        [f"Enrich the investigation input with {', '.join(missing_fields[:3]) or 'another distinguishing clue'} to narrow the target.",
         "Review UNKNOWN and CONTRADICTED comparisons before deciding whether another permitted search is justified."]
    )
    return {
        "investigation_id": investigation_id,
        "status": status,
        "profile": primary,
        "candidate_profiles": profiles,
        "identity_link_count": len(positive_links),
        "unresolved_link_count": len(unresolved_links),
        "contradiction_count": len(contradictions),
        "source_count": len(source_urls),
        "observation_count": len(observations),
        "decision_explanation": {
            "summary": decision_summary,
            "reasons": decision_reasons,
            "next_steps": next_steps,
            "comparison_counts": state_counts,
            "accepted_identity_links": len(positive_links),
            "connected_profile_count": len(resolved_profiles),
        },
        "investigation_input": input_data,
    }
