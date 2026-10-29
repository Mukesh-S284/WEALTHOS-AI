"""Forecasting and Future-Wealth Simulation API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.simulation_service import SimulationService
from backend.schemas.simulation import (
    CashFlowForecastResponse,
    WealthProjectionRequest,
    WealthProjectionResponse,
    MonteCarloSimulationRequest,
    MonteCarloSimulationResponse
)
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/simulation", tags=["Future-Wealth Simulator & Cash-Flow Forecasting"])


@router.get("/cashflow-forecast", response_model=CashFlowForecastResponse)
def get_cashflow_forecast(
    horizon_months: int = Query(6, ge=1, le=36),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Forecast future monthly cash flows using historical transaction trends and moving averages."""
    service = SimulationService(db)
    return service.forecast_cashflow(current_user, horizon_months=horizon_months)


@router.post("/wealth-projection", response_model=WealthProjectionResponse)
def project_future_wealth(
    payload: WealthProjectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deterministic compound interest and wealth projection with inflation adjustment and annual step-up."""
    service = SimulationService(db)
    return service.project_wealth(payload)


@router.post("/monte-carlo", response_model=MonteCarloSimulationResponse)
def run_monte_carlo(
    payload: MonteCarloSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run stochastic Monte Carlo simulation (Geometric Brownian Motion).
    Outputs 10th, 25th, 50th, 75th, 90th percentile distributions and probability of meeting target wealth.
    """
    service = SimulationService(db)
    return service.run_monte_carlo(payload)
