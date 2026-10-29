"""Unit tests for Scam and Fraud Awareness detector."""

from backend.services.scam_service import ScamDetectorService
from backend.schemas.scam import ScamAnalysisRequest


def test_scam_detector_identifies_guaranteed_returns():
    service = ScamDetectorService()
    req = ScamAnalysisRequest(
        message_text="Join our VIP trading pool! 100% risk-free guaranteed returns of 30% weekly profit! You can't lose!"
    )
    res = service.analyze_claim(req)
    
    assert res.threat_score >= 35
    assert res.risk_level in ("HIGH_RISK", "CRITICAL_SCAM")
    categories = [f.category for f in res.detected_red_flags]
    assert "guaranteed_returns" in categories
    assert len(res.official_verification_steps) > 0


def test_scam_detector_identifies_credential_phishing():
    service = ScamDetectorService()
    req = ScamAnalysisRequest(
        message_text="WealthOS Support: We detected suspicious activity. Please share your OTP and private seed phrase to verify identity."
    )
    res = service.analyze_claim(req)

    assert res.threat_score >= 40
    assert res.risk_level in ("HIGH_RISK", "CRITICAL_SCAM")
    categories = [f.category for f in res.detected_red_flags]
    assert "credential_request" in categories


def test_scam_detector_identifies_fomo_and_ponzi():
    service = ScamDetectorService()
    req = ScamAnalysisRequest(
        message_text="Act now before window closes! Only 3 spots left! Recruit 5 friends to earn downline commission from their deposits."
    )
    res = service.analyze_claim(req)

    categories = [f.category for f in res.detected_red_flags]
    assert "urgency_fomo" in categories
    assert "referral_ponzi" in categories
    assert res.threat_score >= 40


def test_scam_detector_safe_investment_claim():
    service = ScamDetectorService()
    req = ScamAnalysisRequest(
        message_text="Vanguard Total Stock Market Index Fund (VTI) tracks the CRSP US Total Market Index with a low expense ratio of 0.03%. Past performance does not guarantee future results."
    )
    res = service.analyze_claim(req)

    assert res.threat_score <= 15
    assert res.risk_level in ("SAFE", "LOW_RISK")
    assert len(res.detected_red_flags) == 0
