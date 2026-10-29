"""User profile and settings schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    preferred_currency: str
    locale: str
    timezone: str
    theme: str
    monthly_income: str
    risk_tolerance: str
    custom_settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    preferred_currency: Optional[str] = Field(None, min_length=3, max_length=3)
    locale: Optional[str] = None
    timezone: Optional[str] = None
    theme: Optional[str] = None
    monthly_income: Optional[str] = None
    risk_tolerance: Optional[str] = None
    custom_settings: Optional[Dict[str, Any]] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class DataExportResponse(BaseModel):
    user_id: str
    export_timestamp: datetime
    user_profile: Dict[str, Any]
    transactions: list
    budgets: list
    savings_goals: list
    debts: list
    portfolios: list
    scenarios: list
