"""Scam and Fraud Awareness schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ScamAnalysisRequest(BaseModel):
    message_text: str = Field(..., min_length=5, max_length=5000, description="Investment pitch, message, email, or offer to analyze")


class WarningFlagItem(BaseModel):
    category: str # guaranteed_returns, urgency_fomo, credential_request, referral_ponzi, unverified_crypto
    severity: str # critical, high, medium, low
    phrase_matched: str
    explanation: str


class ScamAnalysisResponse(BaseModel):
    risk_level: str # SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL_SCAM
    threat_score: int # 0 to 100
    detected_red_flags: List[WarningFlagItem]
    recommendation: str
    official_verification_steps: List[str]
    disclaimer: str
