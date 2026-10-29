"""Market Data Pydantic schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class InstrumentSearchItem(BaseModel):
    symbol: str
    name: str
    exchange: Optional[str] = None
    asset_class: str
    currency: str = "USD"


class QuoteResponse(BaseModel):
    symbol: str
    name: Optional[str] = None
    price: Decimal
    change: Decimal
    change_pct: float
    currency: str
    asset_class: str
    timestamp: datetime
    source: str
    is_delayed: bool


class HistoricalBarItem(BaseModel):
    date: date
    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    close: Decimal
    volume: Optional[int] = None


class HistoricalSeriesResponse(BaseModel):
    symbol: str
    currency: str
    source: str
    start_date: date
    end_date: date
    data_freshness: datetime
    bars: List[HistoricalBarItem]


class AssetClassEducation(BaseModel):
    key: str
    name: str
    description: str
    typical_risk_profile: str
    expected_volatility: str
    role_in_portfolio: str
    liquidity: str
    common_benchmarks: List[str]
