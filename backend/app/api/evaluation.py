from fastapi import APIRouter, HTTPException

from app.evidence_pipeline.evaluation.verification import run_verification_evaluation
from app.evidence_pipeline.evaluation.comparison import run_comparison_evaluation
from app.core.config import get_settings

router = APIRouter(prefix="/evaluations", tags=["evaluation"])


@router.post("/verification")
def evaluate_verification() -> dict:
    return run_verification_evaluation()


@router.get("/verification")
def get_verification_evaluation() -> dict:
    return run_verification_evaluation()


@router.post("/comparison")
def compare_with_baseline() -> dict:
    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is required for the direct baseline")
    return run_comparison_evaluation(settings.openai_api_key, settings.openai_extraction_model, settings.request_timeout_seconds)
