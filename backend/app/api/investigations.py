from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings
from app.core.ids import require_investigation_id
from app.evidence_pipeline.contracts.inputs import PersonClues
from app.evidence_pipeline.orchestration.service import EvidencePipelineService
from app.evidence_pipeline.persistence.sqlite import SQLiteEvidenceRepository
from app.evidence_pipeline.persistence.postgres import PostgresEvidenceRepository
from app.evidence_pipeline.extraction.openai_extractor import OpenAIObservationExtractor
from app.evidence_pipeline.providers.github import GitHubRetriever
from app.evidence_pipeline.providers.tavily import TavilyDiscovery
from app.evidence_pipeline.retrieval.web import WebPageRetriever
from app.evidence_pipeline.retrieval.relevance import matches_identity
from app.evidence_pipeline.extraction.normalization import normalize_observations
from app.evidence_pipeline.contracts.evidence import Observation
from app.evidence_pipeline.normalization.observations import normalize_observation
from app.evidence_pipeline.resolution.candidates import generate_candidate_pairs
from app.evidence_pipeline.orchestration.artifacts import load_latest_run_artifact

router = APIRouter(prefix="/investigations", tags=["investigations"])
_repository = None
_repository_url = None


def build_service(settings: Settings) -> EvidencePipelineService:
    if not settings.tavily_api_key:
        raise HTTPException(status_code=503, detail="TAVILY_API_KEY is required to run discovery")
    repository = _repository_for(settings)
    extractor = (
        OpenAIObservationExtractor(settings.openai_api_key, settings.openai_extraction_model)
        if settings.openai_api_key
        else None
    )
    return EvidencePipelineService(
        discovery=TavilyDiscovery(settings.tavily_api_key, settings.tavily_base_url, settings.request_timeout_seconds),
        retrievers=[
            GitHubRetriever(settings.github_token, settings.github_api_url, settings.request_timeout_seconds),
            WebPageRetriever(settings.request_timeout_seconds),
        ],
        repository=repository,
        extractor=extractor,
        run_repository=repository,
        max_rounds=settings.max_search_rounds,
        max_queries_per_round=settings.max_queries_per_round,
        max_results_per_query=settings.max_results_per_query,
        retry_attempts=settings.provider_retry_attempts,
        source_cache_ttl_hours=settings.source_cache_ttl_hours,
    )


@router.post("")
async def create_investigation(
    clues: PersonClues,
    force_refresh: bool = False,
    investigation_id: str | None = None,
    settings: Settings = Depends(get_settings),
) -> dict:
    if investigation_id:
        investigation_id = require_investigation_id(investigation_id)
    return await build_service(settings).run(
        clues, investigation_id=investigation_id, force_refresh=force_refresh
    )


def _link_counts(verification: dict | None) -> tuple[int, int]:
    results = (verification or {}).get("results") or []
    links = [item for item in results if item.get("comparison_type") == "identity_link"]
    verified = sum(1 for item in links if item.get("state") in {"VERIFIED", "PROBABLE"})
    unresolved = sum(1 for item in links if item.get("state") == "UNKNOWN")
    return verified, unresolved


@router.get("")
def list_investigations(settings: Settings = Depends(get_settings)) -> list[dict]:
    repository = _repository_for(settings)
    items = []
    for item in repository.list_investigations():
        clues = item["clues"]
        investigation_id = item["investigation_id"]
        verification = (
            repository.get_verification(investigation_id)
            if hasattr(repository, "get_verification")
            else None
        )
        verified, unresolved = _link_counts(verification)
        source_count = item.get("source_count")
        if source_count is None:
            source_count = len(repository.get_sources(investigation_id))
        items.append({
            "investigation_id": investigation_id,
            "name": clues.get("name") or "Unnamed investigation",
            "occupation": clues.get("occupation"),
            "status": "saved",
            "reason": "Saved investigation; open to inspect evidence",
            "created_at": item["created_at"],
            "source_count": source_count,
            "verified_link_count": verified,
            "unresolved_comparison_count": unresolved,
        })
    return items


def _require_existing(repository, investigation_id: str) -> str:
    investigation_id = require_investigation_id(investigation_id)
    if repository.get_investigation_clues(investigation_id) is None:
        raise HTTPException(status_code=404, detail="investigation not found")
    return investigation_id


@router.get("/{investigation_id}/sources")
def get_sources(investigation_id: str, settings: Settings = Depends(get_settings)) -> list[dict]:
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    return repository.get_sources(investigation_id)


@router.get("/{investigation_id}/input")
def get_investigation_input(investigation_id: str, settings: Settings = Depends(get_settings)) -> dict:
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    return {"investigation_id": investigation_id, "input": repository.get_investigation_clues(investigation_id) or {}}


@router.put("/{investigation_id}")
async def update_investigation(
    investigation_id: str,
    clues: PersonClues,
    force_refresh: bool = True,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Replace clues and rerun an existing investigation under the same ID."""
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    return await build_service(settings).run(
        clues,
        investigation_id=investigation_id,
        force_refresh=force_refresh,
    )


@router.get("/{investigation_id}/run")
def get_latest_run(investigation_id: str) -> dict:
    investigation_id = require_investigation_id(investigation_id)
    return load_latest_run_artifact(investigation_id) or {
        "investigation_id": investigation_id,
        "status": "not_found",
        "trajectory": [],
    }


@router.get("/{investigation_id}/observations")
def get_observations(investigation_id: str, settings: Settings = Depends(get_settings)) -> list[dict]:
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    return repository.get_observations(investigation_id)


@router.get("/{investigation_id}/normalized-observations")
def get_normalized_observations(investigation_id: str, settings: Settings = Depends(get_settings)) -> list[dict]:
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    observations = [Observation.model_validate(item) for item in repository.get_observations(investigation_id)]
    return [normalize_observation(item).model_dump(mode="json") for item in observations]


@router.get("/{investigation_id}/candidates")
def get_candidates(investigation_id: str, settings: Settings = Depends(get_settings)) -> list[dict]:
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    observations = [Observation.model_validate(item) for item in repository.get_observations(investigation_id)]
    normalized = [normalize_observation(item) for item in observations]
    return [item.model_dump(mode="json") for item in generate_candidate_pairs(normalized)]


@router.post("/{investigation_id}/observations")
async def regenerate_observations(investigation_id: str, settings: Settings = Depends(get_settings)) -> dict:
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    clues = PersonClues.model_validate(repository.get_investigation_clues(investigation_id))
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is required for re-extraction")
    extractor = OpenAIObservationExtractor(settings.openai_api_key, settings.openai_extraction_model)
    observations = []
    for source in repository.get_relevant_sources(investigation_id):
        extracted = normalize_observations(await extractor.extract(source, clues))
        observations.extend(
            item
            for item in extracted
            if matches_identity(item.subject_text, clues) or matches_identity(item.quote, clues)
        )
    await repository.save_investigation_observations(investigation_id, observations)
    return {
        "investigation_id": investigation_id,
        "observation_count": len(observations),
        "status": "reextracted",
        "observations": repository.get_observations(investigation_id),
    }


def _repository_for(settings: Settings):
    global _repository, _repository_url
    if _repository is not None and _repository_url == settings.database_url:
        return _repository
    _repository = (
        PostgresEvidenceRepository(settings.database_url)
        if settings.database_url.startswith(("postgresql://", "postgres://"))
        else SQLiteEvidenceRepository(settings.database_url)
    )
    _repository_url = settings.database_url
    return _repository
