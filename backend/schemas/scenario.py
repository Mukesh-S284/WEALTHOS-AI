"""Life-Event Scenario and Simulation schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class LifeEventScenarioRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    event_type: str = Field(
        ...,
        description="'reduced_income', 'job_transition', 'expense_increase', 'education_costs', 'vehicle_purchase', 'unexpected_medical', 'temporary_income_loss'"
    )
    monthly_income_delta: Decimal = Field(Decimal("0.00"), description="Positive or negative monthly income change")
    monthly_expense_delta: Decimal = Field(Decimal("0.00"), description="Positive or negative recurring expense change")
    one_time_cost: Decimal = Field(Decimal("0.00"), ge=0, description="Upfront lump-sum expense")
    duration_months: int = Field(12, ge=1, le=120, description="Months this event affects finances")
    notes: Optional[str] = None


class ScenarioImpactItem(BaseModel):
    month: int
    baseline_cash_balance: Decimal
    scenario_cash_balance: Decimal
    difference: Decimal


class LifeEventScenarioResponse(BaseModel):
    id: Optional[str] = None
    title: str
    event_type: str
    baseline_monthly_surplus: Decimal
    scenario_monthly_surplus: Decimal
    total_one_time_impact: Decimal
    total_recurring_impact: Decimal
    net_wealth_impact: Decimal
    emergency_buffer_impact_months: float
    is_sustainable: bool
    summary_verdict: str
    monthly_projections: List[ScenarioImpactItem]
