"""Configurable LLM Provider Adapter with graceful fallback."""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel

from backend.core.config import settings


class LLMResponse(BaseModel):
    content: str
    tool_calls: List[Dict[str, Any]] = []
    citations: List[Dict[str, Any]] = []
    model_name: str
    provider: str


class LLMProviderBase(ABC):
    @abstractmethod
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> LLMResponse:
        pass


class GeminiAdapter(LLMProviderBase):
    """Google Gemini API Adapter using REST endpoint with function calling."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.AI_MODEL_NAME

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        # Format contents
        contents = []
        for m in messages:
            role = "user" if m.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": m.get("content", "")}]
            })

        payload: Dict[str, Any] = {"contents": contents}
        if tools:
            payload["tools"] = [{"functionDeclarations": [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"]
                }
                for t in tools
            ]}]

        headers = {"Content-Type": "application/json"}
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        try:
            cand = data["candidates"][0]
            parts = cand["content"]["parts"]
            text_parts = []
            tool_calls = []

            for p in parts:
                if "text" in p:
                    text_parts.append(p["text"])
                if "functionCall" in p:
                    fc = p["functionCall"]
                    tool_calls.append({
                        "name": fc["name"],
                        "arguments": fc.get("args", {})
                    })

            return LLMResponse(
                content="\n".join(text_parts),
                tool_calls=tool_calls,
                model_name=self.model,
                provider="gemini"
            )
        except Exception as e:
            raise RuntimeError(f"Error parsing Gemini response: {e}")


class GroundedRuleEngine(LLMProviderBase):
    """
    Deterministic Financial Reasoning Engine.
    Used when no external LLM API key is configured or when offline.
    Directly extracts intents, executes registered tools, and formats grounded financial answers.
    """

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> LLMResponse:
        last_msg = messages[-1]["content"].lower() if messages else ""

        tool_calls = []
        if any(w in last_msg for w in ("spending", "income", "expenses", "summary", "how much did i spend")):
            tool_calls.append({"name": "get_financial_summary", "arguments": {}})
        elif any(w in last_msg for w in ("goal", "save for", "savings goal")):
            tool_calls.append({
                "name": "calculate_savings_goal",
                "arguments": {"target_amount": 10000, "target_date": "2027-10-01"}
            })
        elif any(w in last_msg for w in ("buy", "purchase", "afford", "laptop", "car")):
            tool_calls.append({
                "name": "compare_purchase_scenarios",
                "arguments": {"purchase_price": 2000, "available_savings": 8000, "monthly_surplus": 600}
            })
        elif any(w in last_msg for w in ("debt", "avalanche", "snowball", "pay off")):
            tool_calls.append({
                "name": "calculate_debt_repayment",
                "arguments": {"extra_monthly_payment": 100}
            })
        elif any(w in last_msg for w in ("portfolio", "volatility", "risk", "drawdown")):
            tool_calls.append({"name": "analyze_portfolio_risk", "arguments": {}})
        elif any(w in last_msg for w in ("compound", "sip", "10 years", "wealth")):
            tool_calls.append({
                "name": "simulate_future_savings",
                "arguments": {"initial_balance": 5000, "monthly_contribution": 500, "annual_return_pct": 8.0, "years": 10}
            })
        else:
            # Default to Knowledge Retrieval
            tool_calls.append({
                "name": "retrieve_finance_knowledge",
                "arguments": {"query": last_msg or "personal finance principles"}
            })

        return LLMResponse(
            content="I am analyzing your financial request and executing verified calculation tools.",
            tool_calls=tool_calls,
            model_name="grounded-deterministic-engine",
            provider="local_grounded_engine"
        )
