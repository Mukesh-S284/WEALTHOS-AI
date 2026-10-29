"""Debt management and payoff simulation API routes."""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from decimal import Decimal
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.debt_service import DebtService
from backend.schemas.debt import (
    DebtCreate,
    DebtUpdate,
    DebtResponse,
    DebtPayoffSimulationRequest,
    DebtPayoffSimulationResponse
)
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/debts", tags=["Debts & Repayment Strategies"])


@router.post("/", response_model=DebtResponse, status_code=status.HTTP_201_CREATED)
def create_debt(
    payload: DebtCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a debt liability (credit card, student loan, personal loan, mortgage)."""
    service = DebtService(db)
    return service.create_debt(current_user, payload)


@router.get("/", response_model=List[DebtResponse])
def list_debts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user debts."""
    service = DebtService(db)
    return service.list_debts(current_user)


@router.get("/{debt_id}", response_model=DebtResponse)
def get_debt(
    debt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single debt liability."""
    service = DebtService(db)
    return service.get_debt(current_user, debt_id)


@router.put("/{debt_id}", response_model=DebtResponse)
def update_debt(
    debt_id: str,
    payload: DebtUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update debt balance, interest rate, or payments."""
    service = DebtService(db)
    return service.update_debt(current_user, debt_id, payload)


@router.delete("/{debt_id}")
def delete_debt(
    debt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a debt liability."""
    service = DebtService(db)
    service.delete_debt(current_user, debt_id)
    return {"message": "Debt liability removed successfully."}


@router.post("/simulate-payoff", response_model=DebtPayoffSimulationResponse)
def simulate_payoff(
    payload: DebtPayoffSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulate and compare Avalanche vs Snowball payoff strategies with optional extra monthly payment."""
    service = DebtService(db)
    return service.simulate_payoff(current_user, extra_payment=payload.extra_monthly_payment)
