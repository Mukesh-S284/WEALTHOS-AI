"""Authentication schemas for request and response validation."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = Field(None, max_length=150)
    preferred_currency: str = Field("USD", min_length=3, max_length=3)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user_id: str
    email: str
    full_name: Optional[str] = None
    preferred_currency: str = "USD"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
