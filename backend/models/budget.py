"""Budget database models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    category = Column(String(100), nullable=False)
    monthly_limit = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    period = Column(String(7), nullable=False) # e.g. "2026-10" or "ALL" for recurring default
    alert_threshold_percentage = Column(Numeric(5, 2), default=80.0, nullable=False) # Alert at 80%
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="budgets")

    __table_args__ = (
        Index("idx_budget_user_period_cat", "user_id", "period", "category", unique=True),
    )
