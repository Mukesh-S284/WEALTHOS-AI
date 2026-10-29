"""Simulation, Projections, and Forecasting Service."""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from backend.models.user import User
from backend.models.transaction import Transaction
from backend.schemas.simulation import (
    CashFlowForecastResponse,
    WealthProjectionRequest,
    WealthProjectionResponse,
    MonteCarloSimulationRequest,
    MonteCarloSimulationResponse
)
from finance_engine.forecasting.cashflow import forecast_monthly_cashflow
from finance_engine.simulation.wealth_projection import calculate_wealth_projection
from finance_engine.simulation.monte_carlo import run_monte_carlo_simulation


class SimulationService:
    def __init__(self, db: Session):
        self.db = db

    def forecast_cashflow(self, user: User, horizon_months: int = 6) -> CashFlowForecastResponse:
        """Fetch user's monthly income and expense history and run forecast."""
        # Query monthly income totals
        income_query = self.db.query(
            extract("year", Transaction.date).label("yr"),
            extract("month", Transaction.date).label("mo"),
            func.sum(Transaction.amount).label("total")
        ).filter(
            Transaction.user_id == user.id,
            Transaction.type == "income"
        ).group_by("yr", "mo").order_by("yr", "mo").all()

        # Query monthly expense totals
        expense_query = self.db.query(
            extract("year", Transaction.date).label("yr"),
            extract("month", Transaction.date).label("mo"),
            func.sum(Transaction.amount).label("total")
        ).filter(
            Transaction.user_id == user.id,
            Transaction.type == "expense"
        ).group_by("yr", "mo").order_by("yr", "mo").all()

        incomes = [float(r.total) for r in income_query]
        expenses = [float(r.total) for r in expense_query]

        # If user has zero records, default to user profile monthly income and 50% expenses
        if not incomes:
            inc = float(user.monthly_income) if float(user.monthly_income) > 0 else 5000.0
            incomes = [inc]
        if not expenses:
            exp = float(user.monthly_income) * 0.5 if float(user.monthly_income) > 0 else 2500.0
            expenses = [exp]

        results = forecast_monthly_cashflow(incomes, expenses, forecast_months=horizon_months)

        return CashFlowForecastResponse(
            forecast_horizon_months=results["forecast_horizon_months"],
            historical_data_points=results["historical_data_points"],
            validation_metrics=results["validation_metrics"],
            projections=results["projections"]
        )

    def project_wealth(self, payload: WealthProjectionRequest) -> WealthProjectionResponse:
        """Run deterministic compound wealth projection."""
        res = calculate_wealth_projection(
            initial_balance=payload.initial_balance,
            monthly_contribution=payload.monthly_contribution,
            annual_return_pct=payload.annual_return_pct,
            annual_inflation_pct=payload.annual_inflation_pct,
            years=payload.years,
            annual_contribution_step_up_pct=payload.annual_contribution_step_up_pct
        )
        return WealthProjectionResponse(**res)

    def run_monte_carlo(self, payload: MonteCarloSimulationRequest) -> MonteCarloSimulationResponse:
        """Run stochastic Monte Carlo simulation with percentiles and target probability."""
        res = run_monte_carlo_simulation(
            initial_wealth=payload.initial_wealth,
            monthly_contribution=payload.monthly_contribution,
            expected_annual_return_pct=payload.expected_annual_return_pct,
            annual_volatility_pct=payload.annual_volatility_pct,
            years=payload.years,
            num_simulations=payload.num_simulations,
            target_wealth=payload.target_wealth,
            annual_inflation_pct=payload.annual_inflation_pct,
            random_seed=payload.random_seed
        )
        return MonteCarloSimulationResponse(**res)
