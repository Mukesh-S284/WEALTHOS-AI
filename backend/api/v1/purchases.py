"""Purchase Affordability Decision Engine API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.purchase_service import PurchaseService
from backend.schemas.purchase import PurchaseEvaluationRequest, PurchaseEvaluationResponse
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/purchases", tags=["Smart Purchase Decision Engine"])


@router.post("/evaluate", response_model=PurchaseEvaluationResponse)
def evaluate_purchase(
    payload: PurchaseEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Evaluate purchase affordability across 5 scenarios:
    1. Buy now cash
    2. Wait and save
    3. Lower cost alternative
    4. Financing / installment
    5. Buffer impact & rebuild timeline
    """
    service = PurchaseService(db)
    return service.evaluate_purchase(current_user, payload)
