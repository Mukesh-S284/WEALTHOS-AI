"""Budget management API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.budget_service import BudgetService
from backend.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetOverviewResponse
)
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/budgets", tags=["Budgets & Spending Limits"])


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def set_budget(
    payload: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update monthly budget for a category."""
    service = BudgetService(db)
    return service.set_budget(current_user, payload)


@router.get("/overview", response_model=BudgetOverviewResponse)
def get_budget_overview(
    period: str = Query(..., description="Format 'YYYY-MM' e.g. '2026-10'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve budget status for a given period with actual transaction spending compared."""
    service = BudgetService(db)
    return service.get_budget_overview(current_user, period=period)


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single budget by ID."""
    service = BudgetService(db)
    return service.get_budget(current_user, budget_id)


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: str,
    payload: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update budget limits and alert thresholds."""
    service = BudgetService(db)
    return service.update_budget(current_user, budget_id, payload)


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a budget."""
    service = BudgetService(db)
    service.delete_budget(current_user, budget_id)
    return {"message": "Budget deleted successfully."}
