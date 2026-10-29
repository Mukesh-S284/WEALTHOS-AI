"""Budget schemas for request/response validation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator


class BudgetBase(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    monthly_limit: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field("USD", min_length=3, max_length=3)
    period: str = Field(..., description="Format 'YYYY-MM' e.g. '2026-10' or 'ALL'")
    alert_threshold_percentage: Decimal = Field(Decimal("80.0"), ge=0, le=100)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.strip().upper()


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    monthly_limit: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    alert_threshold_percentage: Optional[Decimal] = Field(None, ge=0, le=100)


class BudgetResponse(BudgetBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetStatusItem(BaseModel):
    budget_id: str
    category: str
    monthly_limit: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage_used: float
    is_over_budget: bool
    is_near_limit: bool
    currency: str
    period: str


class BudgetOverviewResponse(BaseModel):
    period: str
    currency: str
    total_budgeted: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    overall_percentage_used: float
    items: List[BudgetStatusItem]
