"""Financial Health Reporting API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.report_service import HealthReportService
from backend.schemas.report import FinancialHealthReportResponse
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/reports", tags=["Financial Health Reporting"])


@router.get("/health", response_model=FinancialHealthReportResponse)
def get_health_report(
    period: Optional[str] = Query(None, description="'YYYY-MM'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate transparent Financial Health Report with composite score (0-100),
    evaluating savings rate, liquidity, debt burden, budget adherence, and diversification.
    """
    service = HealthReportService(db)
    return service.generate_health_report(current_user, period=period)
