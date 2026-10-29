"""Scam and Fraud Awareness API routes."""

from fastapi import APIRouter, Depends
from backend.services.scam_service import ScamDetectorService
from backend.schemas.scam import ScamAnalysisRequest, ScamAnalysisResponse
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/scam", tags=["Scam & Fraud Awareness"])


@router.post("/analyze", response_model=ScamAnalysisResponse)
def analyze_claim(
    payload: ScamAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze investment offers, messages, or claims for red flags:
    - Guaranteed risk-free return promises
    - Manufactured urgency and FOMO pressure
    - Credential / password / OTP phishing
    - Multi-level pyramid / Ponzi recruitment schemes
    - Untraceable crypto or gift card payment demands
    """
    service = ScamDetectorService()
    return service.analyze_claim(payload)
