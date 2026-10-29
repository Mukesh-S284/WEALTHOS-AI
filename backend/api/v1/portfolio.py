"""Portfolio Risk Analyzer and Holdings API routes."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.portfolio_service import PortfolioService
from backend.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioHoldingCreate,
    PortfolioHoldingResponse,
    PortfolioRiskReportResponse
)
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/portfolios", tags=["Portfolio Risk Analyzer"])


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    payload: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new investment portfolio."""
    service = PortfolioService(db)
    return service.create_portfolio(current_user, payload)


@router.get("/", response_model=List[PortfolioResponse])
def list_portfolios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user portfolios with live holding values, weights, and asset allocations."""
    service = PortfolioService(db)
    return service.list_portfolios(current_user)


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio valuation and holdings details."""
    service = PortfolioService(db)
    return service.get_portfolio(current_user, portfolio_id)


@router.post("/{portfolio_id}/holdings", response_model=PortfolioHoldingResponse, status_code=status.HTTP_201_CREATED)
def add_holding(
    portfolio_id: str,
    payload: PortfolioHoldingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an investment holding to a portfolio with automatic live market pricing."""
    service = PortfolioService(db)
    return service.add_holding(current_user, portfolio_id, payload)


@router.delete("/{portfolio_id}/holdings/{holding_id}")
def delete_holding(
    portfolio_id: str,
    holding_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a holding from a portfolio."""
    service = PortfolioService(db)
    service.delete_holding(current_user, portfolio_id, holding_id)
    return {"message": "Holding removed successfully."}


@router.get("/{portfolio_id}/risk-report", response_model=PortfolioRiskReportResponse)
def get_portfolio_risk_report(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive portfolio risk report:
    - Asset class diversification & Herfindahl concentration index
    - Annualized volatility, maximum drawdown, and Sharpe ratio
    - Historical stress testing (2008 GFC, 2020 COVID, 2022 Stagflation)
    """
    service = PortfolioService(db)
    return service.generate_risk_report(current_user, portfolio_id)
