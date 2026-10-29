"""WealthOS AI — Frontend API Client.

Centralized HTTP client providing type-safe communication between the Streamlit UI
and the FastAPI backend. Handles authentication headers, session management, and error wrapping.
"""

import os
from typing import Dict, Any, List, Optional
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")


class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        url = base_url.rstrip("/")
        if not url.endswith("/api/v1"):
            url = f"{url}/api/v1"
        self.base_url = url

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            data = response.json()
        except Exception:
            data = {"message": response.text}

        if not response.ok:
            error_msg = data.get("message") or data.get("detail") or f"HTTP {response.status_code}"
            raise Exception(f"API Error ({response.status_code}): {error_msg}")
        return data

    # 1. Auth & User Profile
    def login(self, email: str, password: str) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/auth/login", json={"email": email, "password": password})
        return self._handle_response(resp)

    def register(self, email: str, password: str, full_name: str, preferred_currency: str = "USD") -> Dict[str, Any]:
        payload = {
            "email": email,
            "password": password,
            "full_name": full_name,
            "preferred_currency": preferred_currency
        }
        resp = requests.post(f"{self.base_url}/auth/register", json=payload)
        return self._handle_response(resp)

    def get_me(self, token: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/auth/me", headers=self._headers(token))
        return self._handle_response(resp)

    def update_profile(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.put(f"{self.base_url}/auth/settings", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    def export_user_data(self, token: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/users/export-data", headers=self._headers(token))
        return self._handle_response(resp)

    # 2. Unified Overview & Decision Engine
    def get_overview(self, token: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/decision/overview", headers=self._headers(token))
        return self._handle_response(resp)

    def evaluate_decision(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/decision/evaluate", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    # 3. Money Manager (Transactions & Budgets)
    def list_transactions(self, token: str, limit: int = 100, tx_type: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"limit": limit}
        if tx_type:
            params["type"] = tx_type
        resp = requests.get(f"{self.base_url}/transactions/", params=params, headers=self._headers(token))
        return self._handle_response(resp)

    def create_transaction(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/transactions/", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    def delete_transaction(self, token: str, tx_id: str) -> Dict[str, Any]:
        resp = requests.delete(f"{self.base_url}/transactions/{tx_id}", headers=self._headers(token))
        return self._handle_response(resp)

    def get_transaction_summary(self, token: str, period: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if period:
            params["period"] = period
        resp = requests.get(f"{self.base_url}/transactions/summary", params=params, headers=self._headers(token))
        return self._handle_response(resp)

    def preview_csv_import(self, token: str, csv_content: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/transactions/import/preview",
            json={"csv_content": csv_content},
            headers=self._headers(token)
        )
        return self._handle_response(resp)

    def commit_csv_import(self, token: str, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/transactions/import/commit",
            json={"transactions": transactions},
            headers=self._headers(token)
        )
        return self._handle_response(resp)

    def export_csv(self, token: str) -> str:
        resp = requests.get(f"{self.base_url}/transactions/export/csv", headers=self._headers(token))
        if not resp.ok:
            raise Exception("Failed to export transactions")
        return resp.text

    # 4. Budgets
    def get_budgets_overview(self, token: str, period: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if period:
            params["period"] = period
        resp = requests.get(f"{self.base_url}/budgets/overview", params=params, headers=self._headers(token))
        return self._handle_response(resp)

    def set_budget(self, token: str, category: str, limit_amount: float, period: str) -> Dict[str, Any]:
        payload = {
            "category": category,
            "limit_amount": str(limit_amount),
            "period": period
        }
        resp = requests.post(f"{self.base_url}/budgets/", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    # 5. Savings & Emergency Fund
    def list_savings_goals(self, token: str) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/savings/goals", headers=self._headers(token))
        return self._handle_response(resp)

    def create_savings_goal(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/savings/goals", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    def get_emergency_fund(self, token: str, target_months: int = 6) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/savings/emergency-fund",
            params={"target_months": target_months},
            headers=self._headers(token)
        )
        return self._handle_response(resp)

    # 6. Debts
    def list_debts(self, token: str) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/debts/", headers=self._headers(token))
        return self._handle_response(resp)

    def create_debt(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/debts/", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    def simulate_debt_payoff(self, token: str, extra_monthly: float = 0.0) -> Dict[str, Any]:
        payload = {"extra_monthly_payment": str(extra_monthly)}
        resp = requests.post(f"{self.base_url}/debts/simulate", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    # 7. Market & Portfolio
    def list_portfolios(self, token: str) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/portfolio/", headers=self._headers(token))
        return self._handle_response(resp)

    def create_portfolio(self, token: str, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/portfolio/", json={"name": name, "description": description}, headers=self._headers(token))
        return self._handle_response(resp)

    def add_holding(self, token: str, portfolio_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/portfolio/{portfolio_id}/holdings", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    def get_risk_report(self, token: str, portfolio_id: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/portfolio/{portfolio_id}/risk-report", headers=self._headers(token))
        return self._handle_response(resp)

    def get_market_quote(self, token: str, symbol: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/market/quote/{symbol}", headers=self._headers(token))
        return self._handle_response(resp)

    def get_asset_classes(self, token: str) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/market/asset-classes", headers=self._headers(token))
        return self._handle_response(resp)

    # 8. Forecasting & Simulation
    def forecast_cashflow(self, token: str, horizon_months: int = 12) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/simulation/forecast-cashflow", json={"horizon_months": horizon_months}, headers=self._headers(token))
        return self._handle_response(resp)

    def project_wealth(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/simulation/project-wealth", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    def run_monte_carlo(self, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/simulation/monte-carlo", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    # 9. AI Assistant & Knowledge
    def assistant_chat(self, token: str, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id
        resp = requests.post(f"{self.base_url}/assistant/chat", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    def list_assistant_sessions(self, token: str) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/assistant/sessions", headers=self._headers(token))
        return self._handle_response(resp)

    def search_knowledge(self, token: str, query: str, top_k: int = 3) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/knowledge/search", json={"query": query, "top_k": top_k}, headers=self._headers(token))
        return self._handle_response(resp)

    # 10. Learning & Reporting
    def list_learning_topics(self, token: str) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/learning/topics", headers=self._headers(token))
        return self._handle_response(resp)

    def get_learning_topic(self, token: str, topic_id: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/learning/topics/{topic_id}", headers=self._headers(token))
        return self._handle_response(resp)

    def submit_quiz(self, token: str, topic_id: str, selected_answers: Dict[str, int]) -> Dict[str, Any]:
        payload = {"topic_id": topic_id, "selected_answers": selected_answers}
        resp = requests.post(f"{self.base_url}/learning/quiz/submit", json=payload, headers=self._headers(token))
        return self._handle_response(resp)

    def analyze_scam(self, token: str, text: str) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/scam/analyze", json={"message_text": text}, headers=self._headers(token))
        return self._handle_response(resp)

    def get_health_report(self, token: str, period: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if period:
            params["period"] = period
        resp = requests.get(f"{self.base_url}/reports/health", params=params, headers=self._headers(token))
        return self._handle_response(resp)
