"""API routes for the Unified Financial Decision Engine."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.unified_decision_service import UnifiedDecisionService
from backend.schemas.unified_decision import (
    DecisionEvaluationRequest,
    UnifiedDecisionEvaluationResponse,
    UnifiedDashboardOverviewResponse
)
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/decision", tags=["Unified Financial Decision Engine"])


@router.get("/overview", response_model=UnifiedDashboardOverviewResponse)
def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get unified real-time financial health snapshot across all active modules:
    cash flow, emergency liquidity, debt burden, portfolio value, active goals, and health score.
    """
    service = UnifiedDecisionService(db)
    return service.get_dashboard_overview(current_user)


@router.post("/evaluate", response_model=UnifiedDecisionEvaluationResponse)
def evaluate_decision(
    payload: DecisionEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unified multi-pillar decision evaluation connecting:
    - Budget surplus and cash flow stability
    - Emergency buffer depletion and rebuild horizon
    - Debt-to-income (DTI) ratio expansion
    - Competing savings goal delays and contribution reductions
    """
    service = UnifiedDecisionService(db)
    return service.evaluate_decision(current_user, payload)
