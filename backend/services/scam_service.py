"""Scam & Fraud Awareness analysis service."""

import re
from typing import List, Dict, Any
from backend.schemas.scam import (
    ScamAnalysisRequest,
    ScamAnalysisResponse,
    WarningFlagItem
)

# Documented red flag patterns
RED_FLAG_PATTERNS = [
    {
        "category": "guaranteed_returns",
        "severity": "critical",
        "weight": 35,
        "patterns": [
            r"guaranteed\s+(returns?|profit|income|yield|growth)",
            r"100%\s*(risk[- ]free|safe|guaranteed)",
            r"zero\s*risk",
            r"risk[- ]free\s*(profit|return|investment)",
            r"(double|triple)\s+your\s+money\s+(in|within)\s+\d+\s*(days?|hours?|weeks?)",
            r"\d+%\s*(daily|weekly)\s+(roi|return|profit)",
            r"can'?t\s+lose"
        ],
        "explanation": "No legitimate investment is 100% risk-free. High promised returns without risk are the classic hallmark of Ponzi schemes and investment fraud."
    },
    {
        "category": "credential_request",
        "severity": "critical",
        "weight": 40,
        "patterns": [
            r"share\s+(your\s+)?(password|pin|otp|passcode)",
            r"(send|provide)\s+(the\s+)?(otp|one[- ]time\s+password)",
            r"(seed\s*phrase|recovery\s*phrase|private\s*key)",
            r"remote\s+access\s+to\s+your\s+(computer|phone|device)",
            r"install\s+(anydesk|teamviewer)"
        ],
        "explanation": "Legitimate financial institutions and brokers will NEVER ask you to disclose OTPs, banking passwords, or cryptocurrency recovery seed phrases."
    },
    {
        "category": "urgency_fomo",
        "severity": "high",
        "weight": 20,
        "patterns": [
            r"(act|invest|transfer)\s+now\s+before\s+(it'?s\s+too\s+late|window\s+closes)",
            r"only\s+\d+\s+spots?\s+left",
            r"immediate(ly)?\s+wire\s+funds",
            r"limited\s+time\s+exclusive\s+opportunity",
            r"secret\s+algorithm\s+wall\s*street\s+doesn'?t\s+want\s+you\s+to\s+know"
        ],
        "explanation": "Scammers manufacture artificial urgency to pressure victims into making impulsive emotional transfers before they can conduct due diligence."
    },
    {
        "category": "referral_ponzi",
        "severity": "high",
        "weight": 25,
        "patterns": [
            r"recruit\s+\d+\s+(people|friends|members)",
            r"(downline|upline)\s+(commission|bonus)",
            r"multi[- ]level\s*(marketing)?\s+tier",
            r"matrix\s+compensation",
            r"earn\s+passive\s+income\s+from\s+referrals"
        ],
        "explanation": "Schemes prioritizing recruitment commissions over actual product sales are characteristic of illegal pyramid and Ponzi models."
    },
    {
        "category": "unverified_crypto",
        "severity": "high",
        "weight": 30,
        "patterns": [
            r"send\s+\d+(\.\d+)?\s*(btc|eth|crypto)\s+to\s+receive\s+\d+",
            r"(crypto|bitcoin)\s+giveaway\s+double",
            r"untraceable\s+(payment|transfer)",
            r"gift\s+cards?\s+(for|as)\s+payment"
        ],
        "explanation": "Demands for untraceable payments (crypto transfers to unknown addresses, gift cards) cannot be reversed or insured."
    }
]


class ScamDetectorService:
    def analyze_claim(self, payload: ScamAnalysisRequest) -> ScamAnalysisResponse:
        text = payload.message_text
        detected_flags: List[WarningFlagItem] = []
        threat_score = 0

        for rule in RED_FLAG_PATTERNS:
            cat = rule["category"]
            sev = rule["severity"]
            weight = rule["weight"]
            expl = rule["explanation"]

            for pat in rule["patterns"]:
                match = re.search(pat, text, flags=re.IGNORECASE)
                if match:
                    detected_flags.append(
                        WarningFlagItem(
                            category=cat,
                            severity=sev,
                            phrase_matched=match.group(0),
                            explanation=expl
                        )
                    )
                    threat_score += weight
                    break # count once per category

        threat_score = min(100, threat_score)

        if threat_score >= 60:
            risk_level = "CRITICAL_SCAM"
            rec = "DO NOT PROCEED. This pitch displays extreme indicators of investment fraud or credential phishing."
        elif threat_score >= 35:
            risk_level = "HIGH_RISK"
            rec = "HIGH CAUTION ADVISED. Multiple suspicious red flags detected. Do not send money or share information."
        elif threat_score >= 15:
            risk_level = "MEDIUM_RISK"
            rec = "PROCEED WITH SKEPTICISM. Displays aggressive sales tactics or pressure techniques."
        elif threat_score > 0:
            risk_level = "LOW_RISK"
            rec = "Minor promotional language detected. Always verify credentials through independent official channels."
        else:
            risk_level = "SAFE"
            rec = "No standard high-risk scam keywords or credential harvesting phrases detected."

        verification_steps = [
            "Check registration on FINRA BrokerCheck (brokercheck.finra.org) or SEC Action Lookup.",
            "Verify the firm is an authorized broker-dealer or registered investment adviser (IAPD).",
            "Consult the CFTC RED (Registration Deficient) List for unregistered entities.",
            "Never wire money, buy gift cards, or send cryptocurrency to individuals met online or via unsolicited messages."
        ]

        return ScamAnalysisResponse(
            risk_level=risk_level,
            threat_score=threat_score,
            detected_red_flags=detected_flags,
            recommendation=rec,
            official_verification_steps=verification_steps,
            disclaimer="This automated analysis is an educational heuristic tool and does not constitute a legal determination of fraud or an official law-enforcement report."
        )
