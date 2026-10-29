"""Transaction and CSV import/export Pydantic schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class TransactionBase(BaseModel):
    date: date
    description: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Must be a positive decimal amount")
    type: str = Field(..., description="'income' or 'expense'")
    category: str = Field(..., min_length=1, max_length=100)
    currency: str = Field("USD", min_length=3, max_length=3)
    is_recurring: bool = False
    recurrence_interval: Optional[str] = Field(None, description="'daily', 'weekly', 'monthly', 'yearly'")
    notes: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in ("income", "expense"):
            raise ValueError("Transaction type must be 'income' or 'expense'")
        return v_clean

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.strip().upper()


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    type: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_interval: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_clean = v.strip().lower()
            if v_clean not in ("income", "expense"):
                raise ValueError("Transaction type must be 'income' or 'expense'")
            return v_clean
        return None


class TransactionResponse(TransactionBase):
    id: str
    user_id: str
    classification_source: str
    classification_confidence: Optional[float] = None
    is_user_corrected: bool
    source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    type: Optional[str] = None
    category: Optional[str] = None
    is_recurring: Optional[bool] = None
    search: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)


class TransactionSummaryResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_savings: Decimal
    savings_rate_pct: float
    currency: str
    transaction_count: int
    categories_breakdown: Dict[str, Decimal]


class CSVRowValidation(BaseModel):
    row_number: int
    raw_data: Dict[str, Any]
    parsed_transaction: Optional[TransactionCreate] = None
    is_valid: bool
    is_duplicate: bool = False
    errors: List[str] = []
    suggested_category: Optional[str] = None
    category_confidence: Optional[float] = None


class CSVPreviewResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    rows: List[CSVRowValidation]


class CSVCommitRequest(BaseModel):
    rows: List[TransactionCreate]
