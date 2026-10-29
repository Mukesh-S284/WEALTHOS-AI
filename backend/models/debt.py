"""Debt database models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import relationship
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class Debt(Base):
    __tablename__ = "debts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(150), nullable=False)
    debt_type = Column(String(50), default="credit_card", nullable=False) # credit_card, student_loan, mortgage, auto_loan, personal_loan
    principal_amount = Column(Numeric(14, 2), nullable=False)
    current_balance = Column(Numeric(14, 2), nullable=False)
    interest_rate_apr = Column(Numeric(6, 3), nullable=False) # e.g. 18.5 for 18.5%
    minimum_monthly_payment = Column(Numeric(14, 2), nullable=False)
    actual_monthly_payment = Column(Numeric(14, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="debts")

    __table_args__ = (
        Index("idx_debt_user", "user_id"),
    )
