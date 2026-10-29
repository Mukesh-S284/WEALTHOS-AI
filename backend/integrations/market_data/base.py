"""Market Data Provider Abstract Base Class and Data Transfer Objects."""

from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class InstrumentQuote(BaseModel):
    symbol: str
    name: Optional[str] = None
    price: Decimal
    change: Decimal
    change_pct: float
    currency: str = "USD"
    asset_class: str # equity, mutual_fund, bond, gold, crypto, cash_equivalent
    timestamp: datetime
    source: str
    is_delayed: bool = True


class HistoricalPriceBar(BaseModel):
    date: date
    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    close: Decimal
    volume: Optional[int] = None


class HistoricalDataSeries(BaseModel):
    symbol: str
    currency: str
    source: str
    bars: List[HistoricalPriceBar]
    start_date: date
    end_date: date
    data_freshness: datetime


class MarketDataError(Exception):
    """Custom exception raised when market data provider fails or instrument not found."""
    def __init__(self, message: str, provider: str, symbol: Optional[str] = None):
        super().__init__(message)
        self.provider = provider
        self.symbol = symbol


class MarketDataProviderBase(ABC):
    """Abstract interface that all market data adapters must implement."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider service."""
        pass

    @abstractmethod
    def get_quote(self, symbol: str) -> InstrumentQuote:
        """Fetch current or latest end-of-day market quote."""
        pass

    @abstractmethod
    def get_historical_series(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> HistoricalDataSeries:
        """Fetch historical daily OHLCV series for an instrument."""
        pass

    @abstractmethod
    def search_instruments(self, query: str) -> List[Dict[str, Any]]:
        """Search for instruments by symbol or name."""
        pass
