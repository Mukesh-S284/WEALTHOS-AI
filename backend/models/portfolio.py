"""Portfolio and Holding database models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Text, Boolean, Index
from sqlalchemy.orm import relationship
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(100), default="Primary Portfolio", nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=True, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_portfolio_user", "user_id"),
    )


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    symbol = Column(String(30), nullable=False, index=True) # AAPL, BTC, SPY, GLD, VOO, etc.
    name = Column(String(100), nullable=True)
    asset_class = Column(String(30), nullable=False) # equity, mutual_fund, bond, gold, crypto, cash_equivalent
    quantity = Column(Numeric(18, 6), nullable=False)
    average_buy_price = Column(Numeric(14, 4), nullable=False)
    current_price = Column(Numeric(14, 4), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    
    last_price_updated_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    portfolio = relationship("Portfolio", back_populates="holdings")

    __table_args__ = (
        Index("idx_holding_portfolio_symbol", "portfolio_id", "symbol"),
    )
