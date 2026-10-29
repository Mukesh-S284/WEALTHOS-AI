"""Savings Goal and Contribution Pydantic schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class SavingsGoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    target_amount: Decimal = Field(..., gt=0, decimal_places=2)
    current_amount: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2)
    target_date: date
    monthly_contribution: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2)
    priority: str = Field("medium", description="'low', 'medium', 'high', 'critical'")
    category: str = Field("general", description="'emergency_fund', 'retirement', 'purchase', 'vacation', 'education', 'general'")
    expected_annual_return_pct: Decimal = Field(Decimal("0.0"), ge=0, le=100)
    currency: str = Field("USD", min_length=3, max_length=3)
    notes: Optional[str] = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in ("low", "medium", "high", "critical"):
            raise ValueError("Priority must be one of: low, medium, high, critical")
        return v_clean

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.strip().upper()


class SavingsGoalCreate(SavingsGoalBase):
    pass


class SavingsGoalUpdate(BaseModel):
    title: Optional[str] = None
    target_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    current_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    target_date: Optional[date] = None
    monthly_contribution: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    priority: Optional[str] = None
    status: Optional[str] = None # active, completed, paused, archived
    category: Optional[str] = None
    expected_annual_return_pct: Optional[Decimal] = None
    notes: Optional[str] = None


class SavingsContributionCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    date: Optional[date] = None
    notes: Optional[str] = None


class SavingsGoalResponse(SavingsGoalBase):
    id: str
    user_id: str
    status: str
    required_monthly_savings: Decimal
    projected_completion_date: Optional[date] = None
    is_on_track: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmergencyFundResponse(BaseModel):
    target_months: int
    monthly_essential_expenses: Decimal
    target_amount: Decimal
    current_savings: Decimal
    months_covered: float
    gap_amount: Decimal
    health_status: str
