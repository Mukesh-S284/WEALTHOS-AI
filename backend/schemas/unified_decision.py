"""Schemas for the Unified Financial Decision Engine."""

from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.schemas.purchase import PurchaseEvaluationRequest


class CrossGoalImpact(BaseModel):
    goal_id: str
    goal_title: str
    target_amount: Decimal
    current_amount: Decimal
    current_monthly_contribution: Decimal
    new_monthly_contribution: Decimal
    projected_delay_months: int
    impact_summary: str


class EmergencyFundImpact(BaseModel):
    months_before: float
    months_after: float
    months_depleted: float
    rebuild_months: Optional[int] = None
    is_compromised: bool # drops below 3 months


class BudgetImpact(BaseModel):
    monthly_income: Decimal
    monthly_expenses_before: Decimal
    monthly_expenses_after: Decimal
    monthly_surplus_before: Decimal
    monthly_surplus_after: Decimal
    surplus_change: Decimal
    is_cashflow_negative: bool


class DebtImpact(BaseModel):
    dti_pct_before: float
    dti_pct_after: float
    total_monthly_debt_service_before: Decimal
    total_monthly_debt_service_after: Decimal
    is_dti_high_risk: bool # > 36%


class DecisionPurchaseItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    cost: Decimal = Field(..., gt=0)
    financing_option: str = Field("cash", description="'cash' or 'loan'")
    down_payment: Optional[Decimal] = Field(Decimal("0.00"), ge=0)
    loan_interest_rate_pct: Optional[Decimal] = Field(Decimal("6.5"), ge=0)
    loan_term_months: Optional[int] = Field(36, ge=1, le=360)


class DecisionEvaluationRequest(BaseModel):
    decision_type: str = Field(..., description="'expensive_purchase', 'increase_savings_sip', 'extra_debt_payment'")
    # Purchase branch
    purchase: Optional[DecisionPurchaseItem] = None
    # Savings SIP branch
    additional_sip_amount: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    target_goal_id: Optional[str] = None
    # Debt payoff branch
    extra_debt_payment_monthly: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    lump_sum_debt_payment: Optional[Decimal] = Field(None, ge=Decimal("0.00"))
    target_debt_id: Optional[str] = None


class UnifiedDecisionEvaluationResponse(BaseModel):
    decision_type: str
    is_recommended: bool
    recommendation_verdict: str # APPROVED_SAFE, PROCEED_WITH_CAUTION, NOT_RECOMMENDED
    executive_summary: str
    budget_impact: BudgetImpact
    emergency_fund_impact: EmergencyFundImpact
    debt_impact: DebtImpact
    cross_goal_impacts: List[CrossGoalImpact]
    tradeoff_analysis: List[str]
    actionable_alternatives: List[str]
    health_score_before: int
    estimated_health_score_after: int
    disclaimer: str


class UnifiedDashboardOverviewResponse(BaseModel):
    user_id: str
    currency: str
    monthly_income: Decimal
    monthly_expenses: Decimal
    net_monthly_savings: Decimal
    savings_rate_pct: float
    emergency_fund_months: float
    total_debt_balance: Decimal
    debt_to_income_pct: float
    total_portfolio_value: Decimal
    active_goals_count: int
    health_score: int
    health_rating: str
