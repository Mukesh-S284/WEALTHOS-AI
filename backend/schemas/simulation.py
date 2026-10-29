"""Forecasting and Simulation Pydantic schemas."""

from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MonthlyCashFlowProjectionItem(BaseModel):
    month_offset: int
    projected_income: float
    income_lower: float
    income_upper: float
    projected_expenses: float
    expenses_lower: float
    expenses_upper: float
    projected_net_savings: float


class CashFlowForecastResponse(BaseModel):
    forecast_horizon_months: int
    historical_data_points: int
    validation_metrics: Optional[Dict[str, Any]] = None
    projections: List[MonthlyCashFlowProjectionItem]


class WealthProjectionRequest(BaseModel):
    initial_balance: Decimal = Field(..., ge=0, decimal_places=2)
    monthly_contribution: Decimal = Field(..., ge=0, decimal_places=2)
    annual_return_pct: Decimal = Field(..., ge=0, le=100)
    annual_inflation_pct: Decimal = Field(Decimal("2.5"), ge=0, le=50)
    years: int = Field(10, ge=1, le=50)
    annual_contribution_step_up_pct: Decimal = Field(Decimal("0.0"), ge=0, le=50)


class YearlyTrajectoryMilestone(BaseModel):
    year: int
    nominal_balance: float
    real_inflation_adjusted_balance: float
    total_contributed_principal: float
    total_investment_earnings: float
    monthly_contribution_that_year: float


class WealthProjectionResponse(BaseModel):
    initial_balance: float
    initial_monthly_contribution: float
    annual_return_pct: float
    annual_inflation_pct: float
    annual_step_up_pct: float
    years: int
    final_nominal_wealth: float
    final_real_purchasing_power: float
    total_principal_invested: float
    total_compound_gains: float
    yearly_trajectory: List[YearlyTrajectoryMilestone]


class MonteCarloSimulationRequest(BaseModel):
    initial_wealth: Decimal = Field(..., ge=0, decimal_places=2)
    monthly_contribution: Decimal = Field(..., ge=0, decimal_places=2)
    expected_annual_return_pct: Decimal = Field(..., ge=0, le=100)
    annual_volatility_pct: Decimal = Field(..., ge=1, le=150)
    years: int = Field(15, ge=1, le=40)
    num_simulations: int = Field(1000, ge=100, le=5000)
    target_wealth: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    annual_inflation_pct: Decimal = Field(Decimal("2.5"), ge=0, le=30)
    random_seed: Optional[int] = 42


class MonteCarloYearlyPercentiles(BaseModel):
    year: int
    p10_bearish: float
    p25_conservative: float
    p50_median: float
    p75_optimistic: float
    p90_bullish: float
    median_real_purchasing_power: float


class MonteCarloSimulationResponse(BaseModel):
    model_type: str
    assumptions: Dict[str, Any]
    target_wealth: Optional[float] = None
    probability_of_reaching_target_pct: Optional[float] = None
    final_outcomes: Dict[str, float]
    yearly_percentiles: List[MonteCarloYearlyPercentiles]
    disclaimer: str
