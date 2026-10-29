"""Savings Goals and Emergency Fund API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.savings_service import SavingsService
from backend.schemas.savings import (
    SavingsGoalCreate,
    SavingsGoalUpdate,
    SavingsGoalResponse,
    SavingsContributionCreate,
    EmergencyFundResponse
)
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/savings", tags=["Savings Goals & Emergency Fund"])


@router.post("/goals", response_model=SavingsGoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: SavingsGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new savings goal with target date and target amount."""
    service = SavingsService(db)
    return service.create_goal(current_user, payload)


@router.get("/goals", response_model=List[SavingsGoalResponse])
def list_goals(
    status: Optional[str] = Query(None, description="'active', 'completed', 'paused', 'archived'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user savings goals with required monthly contributions and projected completion dates."""
    service = SavingsService(db)
    return service.list_goals(current_user, status=status)


@router.get("/goals/{goal_id}", response_model=SavingsGoalResponse)
def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single savings goal details."""
    service = SavingsService(db)
    return service.get_goal(current_user, goal_id)


@router.put("/goals/{goal_id}", response_model=SavingsGoalResponse)
def update_goal(
    goal_id: str,
    payload: SavingsGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update goal targets, contributions, or status."""
    service = SavingsService(db)
    return service.update_goal(current_user, goal_id, payload)


@router.delete("/goals/{goal_id}")
def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a savings goal."""
    service = SavingsService(db)
    service.delete_goal(current_user, goal_id)
    return {"message": "Savings goal deleted successfully."}


@router.post("/goals/{goal_id}/contribute", response_model=SavingsGoalResponse)
def add_contribution(
    goal_id: str,
    payload: SavingsContributionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add funds/deposit to an active savings goal."""
    service = SavingsService(db)
    return service.add_contribution(current_user, goal_id, payload)


@router.get("/emergency-fund", response_model=EmergencyFundResponse)
def get_emergency_fund_status(
    target_months: int = Query(6, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Evaluate emergency fund coverage against essential monthly expenses."""
    service = SavingsService(db)
    return service.get_emergency_fund_status(current_user, target_months=target_months)
