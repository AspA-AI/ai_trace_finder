from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.business_investigation.contracts import BusinessClues
from app.business_investigation.contracts import BusinessDualTrackResult, BusinessProfileReconstruction
from app.business_investigation.semantic import OpenAIBusinessProfileVerifier
from app.business_investigation.extractor import OpenAIBusinessExtractor
from app.business_investigation.planner import BusinessQueryPlanner
from app.core.config import Settings, get_settings
from app.evidence_pipeline.orchestration.service import EvidencePipelineService
from app.evidence_pipeline.persistence.postgres import PostgresEvidenceRepository
from app.evidence_pipeline.persistence.sqlite import SQLiteEvidenceRepository
from app.evidence_pipeline.providers.github import GitHubRetriever
from app.evidence_pipeline.providers.tavily import TavilyDiscovery
from app.evidence_pipeline.retrieval.web import WebPageRetriever
from app.evidence_pipeline.contracts.evidence import Observation
from app.evidence_pipeline.normalization.observations import normalize_observation
from app.evidence_pipeline.resolution.candidates import generate_candidate_pairs
from app.evidence_pipeline.verification.deterministic import verify_candidates
from app.evidence_pipeline.reporting.synthesis import synthesize_profile
from app.evidence_pipeline.verification.artifacts import save_verification_artifact
from app.evidence_pipeline.verification.dual_track import _aggregate_deterministic

router = APIRouter(prefix="/business-investigations", tags=["business-investigations"])
_repository = None
_repository_url = None


def _repository_for(settings: Settings):
    global _repository, _repository_url
    if _repository is not None and _repository_url == settings.database_url:
        return _repository
    _repository = PostgresEvidenceRepository(settings.database_url) if settings.database_url.startswith(("postgresql://", "postgres://")) else SQLiteEvidenceRepository(settings.database_url)
    _repository_url = settings.database_url
    return _repository


def _service(settings: Settings) -> EvidencePipelineService:
    if not settings.tavily_api_key:
        raise HTTPException(status_code=503, detail="TAVILY_API_KEY is required to run business discovery")
    repository = _repository_for(settings)
    extractor = OpenAIBusinessExtractor(settings.openai_api_key, settings.openai_extraction_model) if settings.openai_api_key else None
    return EvidencePipelineService(
        discovery=TavilyDiscovery(settings.tavily_api_key, settings.tavily_base_url, settings.request_timeout_seconds),
        retrievers=[GitHubRetriever(settings.github_token, settings.github_api_url, settings.request_timeout_seconds), WebPageRetriever(settings.request_timeout_seconds)],
        repository=repository,
        planner=BusinessQueryPlanner(),
        extractor=extractor,
        run_repository=repository,
        max_rounds=settings.max_search_rounds,
        max_queries_per_round=settings.max_queries_per_round,
        max_results_per_query=settings.max_results_per_query,
        retry_attempts=settings.provider_retry_attempts,
        source_cache_ttl_hours=settings.source_cache_ttl_hours,
    )


@router.post("")
async def create_business_investigation(clues: BusinessClues, force_refresh: bool = False, settings: Settings = Depends(get_settings)) -> dict:
    """Run a business evidence collection under a new investigation ID."""
    return await _service(settings).run(clues, investigation_id=f"biz_{uuid4().hex[:12]}", force_refresh=force_refresh)


@router.get("")
def list_business_investigations(settings: Settings = Depends(get_settings)) -> list[dict]:
    """List saved business cases separately from the people workspace."""
    repository = _repository_for(settings)
    items = []
    for item in repository.list_investigations():
        investigation_id = item["investigation_id"]
        if not investigation_id.startswith("biz_"):
            continue
        verification = repository.get_verification(investigation_id) if hasattr(repository, "get_verification") else None
        results = (verification or {}).get("results") or []
        identity_links = [result for result in results if result.get("comparison_type") == "identity_link"]
        accepted = sum(result.get("state") in {"VERIFIED", "PROBABLE"} for result in identity_links)
        unresolved = sum(result.get("state") == "UNKNOWN" for result in identity_links)
        source_count = item.get("source_count")
        if source_count is None:
            source_count = len(repository.get_sources(investigation_id))
        clues = item["clues"]
        items.append({
            "investigation_id": investigation_id,
            "company_name": clues.get("company_name") or clues.get("name") or "Unnamed business",
            "industry": clues.get("industry"),
            "status": "verified" if accepted else "needs_review",
            "reason": "Independent business analysis saved" if verification else "Evidence collected; verification not run",
            "created_at": item["created_at"],
            "source_count": source_count,
            "observation_count": len(repository.get_observations(investigation_id)),
            "verified_link_count": accepted,
            "unresolved_comparison_count": unresolved,
        })
    return sorted(items, key=lambda item: item["created_at"], reverse=True)


def _require_business(repository, investigation_id: str) -> str:
    if not investigation_id.startswith("biz_") or repository.get_investigation_clues(investigation_id) is None:
        raise HTTPException(status_code=404, detail="business investigation not found")
    return investigation_id


@router.get("/{investigation_id}/input")
def get_business_input(investigation_id: str, settings: Settings = Depends(get_settings)) -> dict:
    repository = _repository_for(settings)
    investigation_id = _require_business(repository, investigation_id)
    return {"investigation_id": investigation_id, "input": repository.get_investigation_clues(investigation_id) or {}}


@router.get("/{investigation_id}/sources")
def get_business_sources(investigation_id: str, settings: Settings = Depends(get_settings)) -> list[dict]:
    repository = _repository_for(settings)
    investigation_id = _require_business(repository, investigation_id)
    return repository.get_sources(investigation_id)


@router.get("/{investigation_id}/observations")
def get_business_observations(investigation_id: str, settings: Settings = Depends(get_settings)) -> list[dict]:
    repository = _repository_for(settings)
    investigation_id = _require_business(repository, investigation_id)
    return repository.get_observations(investigation_id)


@router.post("/{investigation_id}/verification")
async def verify_business_investigation(investigation_id: str, settings: Settings = Depends(get_settings)) -> dict:
    """Run two independent business analyses over the same evidence.

    The deterministic track compares source observations. The semantic track
    independently reads the complete observation set and never receives the
    deterministic features or verdicts.
    """
    repository = _repository_for(settings)
    investigation_id = _require_business(repository, investigation_id)
    observations = [Observation.model_validate(item) for item in repository.get_observations(investigation_id)]
    normalized = [normalize_observation(item) for item in observations]
    candidates = generate_candidate_pairs(normalized)
    results = verify_candidates(candidates, normalized)
    result_json = [item.model_dump(mode="json") for item in results]
    clues = repository.get_investigation_clues(investigation_id) or {}
    profile = synthesize_profile(investigation_id, observations, {"results": result_json}, clues)
    deterministic_verdict, deterministic_confidence, deterministic_reasoning = _aggregate_deterministic(results)
    if settings.openai_api_key:
        semantic = await OpenAIBusinessProfileVerifier(
            settings.openai_api_key, settings.openai_extraction_model
        ).analyze(clues, normalized)
        semantic_status = "available"
        if semantic.verdict == "insufficient_evidence" or deterministic_verdict.value == "UNKNOWN":
            agreement = "one_abstained"
        elif (
            deterministic_verdict.value in {"VERIFIED", "PROBABLE"}
            and semantic.verdict == "likely_same_business"
        ) or (
            deterministic_verdict.value == "CONTRADICTED"
            and semantic.verdict == "likely_multiple_businesses"
        ):
            agreement = "aligned"
        else:
            agreement = "diverging"
        suggested_action = None if agreement == "aligned" else (
            "Review the cited observations and add an official domain, repository, founder, or product clue before treating this as one business."
        )
    else:
        semantic = BusinessProfileReconstruction(
            verdict="insufficient_evidence",
            confidence_label="low",
            profile_summary="No independent business profile was generated because the semantic model is unavailable.",
            reasoning="The deterministic comparison is available, but the independent full-evidence business analysis requires OPENAI_API_KEY.",
            caveats=["Enable the semantic model before using the semantic track for review."],
        )
        semantic_status = "unavailable"
        agreement = "one_abstained"
        suggested_action = "Enable the semantic model to obtain the independent full-evidence business analysis."
    dual_track = BusinessDualTrackResult(
        investigation_id=investigation_id,
        deterministic_verdict=deterministic_verdict,
        deterministic_confidence=deterministic_confidence,
        deterministic_reasoning=deterministic_reasoning,
        semantic_verdict=semantic.verdict,
        semantic_confidence=semantic.confidence_label,
        semantic_reasoning=semantic.reasoning,
        semantic_caveats=semantic.caveats,
        semantic_profile=semantic,
        agreement=agreement,
        suggested_action=suggested_action,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    run_id = f"verify_{uuid4().hex[:12]}"
    artifact = save_verification_artifact(investigation_id, {"observations": [item.model_dump(mode="json") for item in observations], "normalized_observations": [item.model_dump(mode="json") for item in normalized], "candidates": [item.model_dump(mode="json") for item in candidates], "deterministic_results": result_json, "profile": profile, "dual_track": dual_track.model_dump(mode="json")}, run_id=run_id)
    response = {"investigation_id": investigation_id, "run_id": run_id, "candidate_count": len(candidates), "verification_count": len(results), "results": result_json, "profile": profile, "dual_track": dual_track.model_dump(mode="json"), "semantic_status": semantic_status, "artifact": artifact}
    if hasattr(repository, "save_verification"):
        await repository.save_verification(investigation_id, run_id, response)
    return response


@router.get("/{investigation_id}/verification")
def get_business_verification(investigation_id: str, settings: Settings = Depends(get_settings)) -> dict:
    repository = _repository_for(settings)
    investigation_id = _require_business(repository, investigation_id)
    return repository.get_verification(investigation_id) if hasattr(repository, "get_verification") and repository.get_verification(investigation_id) else {"investigation_id": investigation_id, "status": "not_run"}
