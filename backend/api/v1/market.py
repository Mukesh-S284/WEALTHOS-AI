"""Market Data and Multi-Asset Intelligence API routes."""

from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.market_service import MarketService
from backend.schemas.market import (
    QuoteResponse,
    HistoricalSeriesResponse,
    InstrumentSearchItem,
    AssetClassEducation
)
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/market", tags=["Multi-Asset Investment Intelligence"])


@router.get("/asset-classes", response_model=List[AssetClassEducation])
def get_asset_classes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Educational details on all supported asset classes (equities, bonds, gold, crypto, savings)."""
    service = MarketService(db)
    return service.get_asset_classes()


@router.get("/quote", response_model=QuoteResponse)
def get_quote(
    symbol: str = Query(..., description="Ticker symbol e.g. 'SPY', 'AAPL', 'BND', 'GLD', 'BTC-USD'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve current or latest market price quote with source attribution and timestamp."""
    service = MarketService(db)
    return service.get_quote(symbol)


@router.get("/historical", response_model=HistoricalSeriesResponse)
def get_historical_series(
    symbol: str = Query(..., description="Ticker symbol"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve historical daily price bars for charting and volatility analysis."""
    today = date.today()
    start = start_date or (today - timedelta(days=365))
    end = end_date or today
    service = MarketService(db)
    return service.get_historical_series(symbol, start, end)


@router.get("/search", response_model=List[InstrumentSearchItem])
def search_instruments(
    query: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for supported financial instruments and ticker symbols."""
    service = MarketService(db)
    return service.search_instruments(query)
