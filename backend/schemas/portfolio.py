"""Portfolio and Holdings schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class PortfolioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    currency: str = Field("USD", min_length=3, max_length=3)
    is_default: bool = True

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.strip().upper()


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None


class PortfolioHoldingCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    name: Optional[str] = None
    asset_class: str = Field("equity", description="equity, mutual_fund, bond, gold, crypto, cash_equivalent")
    quantity: Decimal = Field(..., gt=0, description="Positive holding units")
    average_buy_price: Decimal = Field(..., gt=0, decimal_places=4)
    currency: str = Field("USD", min_length=3, max_length=3)
    notes: Optional[str] = None

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("asset_class")
    @classmethod
    def validate_asset_class(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in ("equity", "mutual_fund", "bond", "gold", "crypto", "cash_equivalent"):
            raise ValueError("Invalid asset_class")
        return v_clean


class PortfolioHoldingUpdate(BaseModel):
    quantity: Optional[Decimal] = Field(None, gt=0)
    average_buy_price: Optional[Decimal] = Field(None, gt=0)
    notes: Optional[str] = None


class PortfolioHoldingResponse(BaseModel):
    id: str
    portfolio_id: str
    symbol: str
    name: Optional[str] = None
    asset_class: str
    quantity: Decimal
    average_buy_price: Decimal
    current_price: Optional[Decimal] = None
    currency: str
    current_value: Optional[Decimal] = None
    unrealized_gain_loss: Optional[Decimal] = None
    gain_loss_pct: Optional[float] = None
    weight_pct: Optional[float] = None
    last_price_updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PortfolioResponse(PortfolioBase):
    id: str
    user_id: str
    total_cost: Decimal
    total_value: Decimal
    total_gain_loss: Decimal
    total_gain_loss_pct: float
    holdings: List[PortfolioHoldingResponse]
    asset_class_allocation_pct: Dict[str, float]
    concentration_hhi: float
    top3_concentration_pct: float
    created_at: datetime
    updated_at: datetime


class StressTestScenarioResult(BaseModel):
    scenario_name: str
    description: str
    estimated_impact_pct: float
    estimated_dollar_impact: Decimal
    projected_portfolio_value: Decimal


class PortfolioRiskReportResponse(BaseModel):
    portfolio_id: str
    portfolio_name: str
    total_value: Decimal
    asset_class_allocation: Dict[str, float]
    concentration_hhi: float
    top3_concentration_pct: float
    annualized_volatility_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float
    stress_scenarios: List[StressTestScenarioResult]
    risk_level_assessment: str
    disclaimer: str
