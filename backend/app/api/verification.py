import json
import logging
from time import perf_counter
from fastapi import APIRouter, Depends
from bs4 import BeautifulSoup
from uuid import uuid4

from app.api.investigations import _repository_for, _require_existing
from app.core.config import Settings, get_settings
from app.evidence_pipeline.verification.hybrid import verify_hybrid
from app.evidence_pipeline.contracts.evidence import Observation
from app.evidence_pipeline.normalization.observations import normalize_observation
from app.evidence_pipeline.resolution.candidates import generate_candidate_pairs
from app.evidence_pipeline.verification.deterministic import verify_candidates
from app.evidence_pipeline.verification.contracts import DualTrackResult, ProfileReconstruction
from app.evidence_pipeline.verification.dual_track import build_dual_track_result
from app.evidence_pipeline.verification.semantic import ConstrainedSemanticVerifier, ProfileReconstructionVerifier
from app.evidence_pipeline.verification.artifacts import save_verification_artifact

router = APIRouter(prefix="/investigations", tags=["verification"])
log = logging.getLogger("trace.verification")


@router.post("/{investigation_id}/verification")
async def run_verification(
    investigation_id: str, settings: Settings = Depends(get_settings)
) -> dict:
    started = perf_counter()
    log.info("verification started investigation_id=%s", investigation_id)
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    observations = [
        Observation.model_validate(item) for item in repository.get_observations(investigation_id)
    ]
    normalized = [normalize_observation(item) for item in observations]
    candidates = generate_candidate_pairs(normalized)
    log.info("verification candidates generated investigation_id=%s observations=%d candidates=%d", investigation_id, len(normalized), len(candidates))
    deterministic_results = verify_candidates(candidates, normalized)
    pair_verifier = (
        ConstrainedSemanticVerifier(settings.openai_api_key, settings.openai_extraction_model)
        if settings.openai_api_key
        else None
    )
    deterministic_results = await verify_hybrid(
        deterministic_results,
        normalized,
        pair_verifier,
        max_comparisons=settings.max_semantic_comparisons,
    )
    log.info("deterministic verification completed investigation_id=%s comparisons=%d", investigation_id, len(deterministic_results))
    clues = repository.get_investigation_clues(investigation_id) or {}
    sources = repository.get_relevant_sources(investigation_id)
    photo_candidates = []
    for source in sources:
        image_url = source.metadata.get("image_url") or _saved_image_url(source)
        if image_url:
            photo_candidates.append(
                {
                    "source_id": source.source_id,
                    "source_url": str(source.url),
                    "image_url": image_url,
                    "observation_ids": [
                        item.observation_id
                        for item in normalized
                        if item.source_id == source.source_id
                    ],
                }
            )
    if settings.openai_api_key:
        profile_verifier = ProfileReconstructionVerifier(
            settings.openai_api_key, settings.openai_extraction_model
        )
        dual_track = await build_dual_track_result(
            investigation_id,
            clues,
            normalized,
            deterministic_results,
            profile_verifier,
            photo_candidates,
        )
        dual_track = _scope_image_candidates(dual_track, photo_candidates)
        log.info("semantic verification completed investigation_id=%s verdict=%s agreement=%s", investigation_id, dual_track.semantic_verdict, dual_track.agreement)
    else:
        dual_track = _semantic_unavailable(investigation_id, deterministic_results)
    stages = {
        "observations": [item.model_dump(mode="json") for item in observations],
        "normalized_observations": [item.model_dump(mode="json") for item in normalized],
        "candidates": [item.model_dump(mode="json") for item in candidates],
        "deterministic_results": [item.model_dump(mode="json") for item in deterministic_results],
        # Kept as an alias for existing artifact readers. These are the
        # deterministic comparison results; the independent semantic track is
        # stored separately below and never overwrites them.
        "final_results": [item.model_dump(mode="json") for item in deterministic_results],
        "dual_track": dual_track.model_dump(mode="json"),
    }
    run_id = f"verify_{uuid4().hex[:12]}"
    artifact = save_verification_artifact(investigation_id, stages, run_id=run_id)
    response = {
        "investigation_id": investigation_id,
        "run_id": run_id,
        "candidate_count": len(candidates),
        "verification_count": len(deterministic_results),
        "results": [item.model_dump(mode="json") for item in deterministic_results],
        "dual_track": dual_track.model_dump(mode="json"),
        "artifact_path": artifact["path"],
        "artifact": artifact,
    }
    if hasattr(repository, "save_verification"):
        await repository.save_verification(investigation_id, run_id, response)
    log.info("verification completed investigation_id=%s run_id=%s elapsed_ms=%.2f", investigation_id, run_id, (perf_counter() - started) * 1000)
    return response


def _scope_image_candidates(
    dual_track: DualTrackResult, photo_candidates: list[dict]
) -> DualTrackResult:
    """The photo gallery is built from every source in the investigation,
    before the profile reconstruction runs, so it has no way to know which
    sources the semantic track later ruled out-of-scope (e.g. a same-name
    collision with far more coverage than the actual target). Re-filter it
    here against the profile's own scope decision so the gallery never shows
    a person the text has already excluded.

    If the profile ended up with no supporting evidence at all (fully
    unresolved), show no images rather than falling back to the unfiltered
    set — an empty gallery is honest; a wrong one is not.
    """
    profile = dual_track.semantic_profile
    if profile is None:
        return dual_track.model_copy(update={"image_candidates": []})

    supporting = set(profile.supporting_observation_ids or [])
    excluded = set(profile.out_of_scope_observation_ids or [])

    def _in_scope(candidate: dict) -> bool:
        obs_ids = set(candidate.get("observation_ids", []))
        if obs_ids & excluded:
            return False
        if supporting and not (obs_ids & supporting):
            return False
        return True

    scoped = [candidate for candidate in photo_candidates if _in_scope(candidate)]
    return dual_track.model_copy(update={"image_candidates": scoped})


def _semantic_unavailable(investigation_id: str, results) -> object:
    """Keep offline/no-key runs explicit instead of pretending there was an LLM read."""
    from datetime import datetime, timezone
    from app.evidence_pipeline.verification.dual_track import _aggregate_deterministic

    verdict, confidence, reasoning = _aggregate_deterministic(results)
    semantic = ProfileReconstruction(
        verdict="insufficient_evidence",
        confidence_label="low",
        profile_summary="No independent semantic profile was generated because the semantic model is unavailable.",
        reasoning="The deterministic analysis is available, but an independent full-evidence semantic analysis requires OPENAI_API_KEY.",
        caveats=["Run with the semantic model enabled before using this track for adjudication."],
    )
    return DualTrackResult(
        investigation_id=investigation_id,
        deterministic_verdict=verdict,
        deterministic_confidence=confidence,
        deterministic_reasoning=reasoning,
        semantic_verdict=semantic.verdict,
        semantic_confidence=semantic.confidence_label,
        semantic_reasoning=semantic.reasoning,
        semantic_caveats=semantic.caveats,
        semantic_profile=semantic,
        image_candidates=[],
        agreement="one_abstained",
        suggested_action="Enable the semantic model to obtain the independent full-evidence analysis.",
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


def _saved_image_url(source) -> str | None:
    """Recover an image candidate from an already captured source snapshot."""
    content = source.raw_content or source.content or ""
    if source.domain == "github.com":
        try:
            value = json.loads(content).get("avatar_url")
            return (
                value
                if isinstance(value, str) and value.startswith(("http://", "https://"))
                else None
            )
        except (TypeError, ValueError):
            return None
    soup = BeautifulSoup(content, "html.parser")
    for attrs in ({"property": "og:image"}, {"name": "twitter:image"}):
        tag = soup.find("meta", attrs=attrs)
        value = tag.get("content", "") if tag else ""
        if value.startswith(("http://", "https://")):
            return value
    return None


@router.get("/{investigation_id}/verification")
def get_verification(investigation_id: str, settings: Settings = Depends(get_settings)) -> dict:
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    result = (
        repository.get_verification(investigation_id)
        if hasattr(repository, "get_verification")
        else None
    )
    return result or {"investigation_id": investigation_id, "status": "not_run"}
