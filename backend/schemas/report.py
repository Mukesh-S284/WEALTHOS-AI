"""Financial Health Reporting schemas."""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class HealthIndicatorItem(BaseModel):
    name: str
    category: str
    score: int # points earned
    max_score: int # points possible
    status: str # excellent, good, fair, poor, missing_data
    metric_value: str
    target_benchmark: str
    explanation: str


class FinancialHealthReportResponse(BaseModel):
    overall_health_score: int # 0 to 100
    rating: str # Excellent, Good, Fair, Needs Attention, Incomplete
    reporting_period: str
    monthly_income: Decimal
    total_expenses: Decimal
    net_savings: Decimal
    savings_rate_pct: float
    indicators: List[HealthIndicatorItem]
    strengths: List[str]
    areas_for_improvement: List[str]
    disclaimer: str
