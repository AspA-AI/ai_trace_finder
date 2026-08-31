from fastapi import APIRouter, Depends, HTTPException

from app.api.investigations import _repository_for, _require_existing
from app.core.config import Settings, get_settings
from app.evidence_pipeline.contracts.evidence import Observation
from app.evidence_pipeline.reporting.synthesis import synthesize_profile

router = APIRouter(prefix="/investigations", tags=["reporting"])


@router.post("/{investigation_id}/profile")
async def generate_profile(investigation_id: str, settings: Settings = Depends(get_settings)) -> dict:
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    clues = repository.get_investigation_clues(investigation_id) if hasattr(repository, "get_investigation_clues") else None
    verification = repository.get_verification(investigation_id) if hasattr(repository, "get_verification") else None
    if not verification:
        raise HTTPException(status_code=409, detail="verification_required")
    observations = [Observation.model_validate(item) for item in repository.get_observations(investigation_id)]
    profile = synthesize_profile(investigation_id, observations, verification, clues)
    if hasattr(repository, "save_profile"):
        await repository.save_profile(investigation_id, profile)
    return profile


@router.get("/{investigation_id}/profile")
def get_profile(investigation_id: str, settings: Settings = Depends(get_settings)) -> dict:
    repository = _repository_for(settings)
    investigation_id = _require_existing(repository, investigation_id)
    profile = repository.get_profile(investigation_id) if hasattr(repository, "get_profile") else None
    clues = repository.get_investigation_clues(investigation_id) if hasattr(repository, "get_investigation_clues") else None
    verification = repository.get_verification(investigation_id) if hasattr(repository, "get_verification") else None
    if verification:
        observations = [Observation.model_validate(item) for item in repository.get_observations(investigation_id)]
        return synthesize_profile(investigation_id, observations, verification, clues)
    if profile and clues is not None:
        profile["investigation_input"] = clues
    return profile or {"investigation_id": investigation_id, "status": "not_generated", "investigation_input": clues or {}}
