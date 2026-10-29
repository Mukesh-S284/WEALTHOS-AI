"""Market Data and Instrument database models."""

import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Numeric, DateTime, Date, BigInteger, Boolean, JSON, Index
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class SupportedInstrument(Base):
    __tablename__ = "supported_instruments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    asset_class = Column(String(30), nullable=False) # equity, mutual_fund, bond, gold, crypto, cash_equivalent
    exchange = Column(String(50), nullable=True) # NASDAQ, NYSE, Crypto, etc.
    currency = Column(String(3), default="USD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata_info = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)


class MarketObservation(Base):
    __tablename__ = "market_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(30), nullable=False, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    
    open_price = Column(Numeric(14, 4), nullable=True)
    high_price = Column(Numeric(14, 4), nullable=True)
    low_price = Column(Numeric(14, 4), nullable=True)
    close_price = Column(Numeric(14, 4), nullable=False)
    volume = Column(BigInteger, nullable=True)
    
    source = Column(String(50), nullable=False) # 'yahoo_finance', 'coingecko', 'alphavantage', etc.
    fetched_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("idx_obs_symbol_date", "symbol", "observation_date", unique=True),
    )
