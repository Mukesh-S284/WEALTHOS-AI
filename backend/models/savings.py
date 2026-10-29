"""Savings Goal database models."""

import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Date, Text, Index
from sqlalchemy.orm import relationship
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(150), nullable=False)
    target_amount = Column(Numeric(14, 2), nullable=False)
    current_amount = Column(Numeric(14, 2), default=0.0, nullable=False)
    target_date = Column(Date, nullable=False)
    
    monthly_contribution = Column(Numeric(14, 2), default=0.0, nullable=False)
    priority = Column(String(20), default="medium", nullable=False) # low, medium, high, critical
    status = Column(String(20), default="active", nullable=False) # active, completed, paused, archived
    category = Column(String(50), default="general", nullable=False) # emergency_fund, retirement, purchase, vacation, education
    
    expected_annual_return_pct = Column(Numeric(5, 2), default=0.0, nullable=False) # 0 for cash, e.g. 5.0 for conservative investment
    currency = Column(String(3), default="USD", nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="savings_goals")
    contributions = relationship("SavingsContribution", back_populates="goal", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_savings_user_status", "user_id", "status"),
    )


class SavingsContribution(Base):
    __tablename__ = "savings_contributions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = Column(String(36), ForeignKey("savings_goals.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    amount = Column(Numeric(14, 2), nullable=False)
    date = Column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    goal = relationship("SavingsGoal", back_populates="contributions")
