"""Purchase Affordability Pydantic schemas."""

from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class PurchaseEvaluationRequest(BaseModel):
    purchase_price: Decimal = Field(..., gt=0, decimal_places=2)
    available_liquid_savings: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    monthly_net_surplus: Optional[Decimal] = Field(None, decimal_places=2)
    minimum_cash_buffer: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    financing_apr: Decimal = Field(Decimal("9.99"), ge=0, le=100)
    financing_tenure_months: int = Field(12, ge=1, le=120)
    alternative_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class PurchaseEvaluationResponse(BaseModel):
    purchase_price: Decimal
    available_liquid_savings: Decimal
    monthly_net_surplus: Decimal
    minimum_cash_buffer: Decimal
    verdict: str
    verdict_summary: str
    scenarios: Dict[str, Any]
