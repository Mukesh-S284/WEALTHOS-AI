"""Debt schemas for request/response validation and payoff simulation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class DebtBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    debt_type: str = Field("credit_card", description="credit_card, student_loan, mortgage, auto_loan, personal_loan")
    principal_amount: Decimal = Field(..., gt=0, decimal_places=2)
    current_balance: Decimal = Field(..., ge=0, decimal_places=2)
    interest_rate_apr: Decimal = Field(..., ge=0, decimal_places=3)
    minimum_monthly_payment: Decimal = Field(..., gt=0, decimal_places=2)
    actual_monthly_payment: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    currency: str = Field("USD", min_length=3, max_length=3)
    notes: Optional[str] = None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.strip().upper()


class DebtCreate(DebtBase):
    pass


class DebtUpdate(BaseModel):
    name: Optional[str] = None
    debt_type: Optional[str] = None
    current_balance: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    interest_rate_apr: Optional[Decimal] = Field(None, ge=0)
    minimum_monthly_payment: Optional[Decimal] = Field(None, gt=0)
    actual_monthly_payment: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class DebtResponse(DebtBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DebtPayoffSimulationRequest(BaseModel):
    extra_monthly_payment: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2)


class StrategyOutcome(BaseModel):
    strategy: str
    total_months: int
    total_interest_paid: Decimal
    total_principal_paid: Decimal
    total_paid: Decimal
    debts_payoff_order: List[Dict[str, Any]]


class DebtPayoffSimulationResponse(BaseModel):
    avalanche: StrategyOutcome
    snowball: StrategyOutcome
    avalanche_interest_savings: Decimal
    avalanche_months_saved: int
    recommendation: str
