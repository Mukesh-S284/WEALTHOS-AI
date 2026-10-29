"""Transaction and Category database models."""

import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Boolean, DateTime, Date, Numeric, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False) # income, expense
    icon = Column(String(50), default="tag", nullable=False)
    color = Column(String(20), default="#4E79A7", nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("idx_category_user_name", "user_id", "name"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Financial details
    date = Column(Date, nullable=False, index=True)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False) # Positive value
    type = Column(String(20), nullable=False) # 'income' or 'expense'
    category = Column(String(100), nullable=False, index=True)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Recurring and subscription tracking
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_interval = Column(String(20), nullable=True) # daily, weekly, monthly, yearly
    
    # Classification metadata
    classification_source = Column(String(50), default="manual", nullable=False) # manual, rule, ml, import
    classification_confidence = Column(Numeric(5, 4), nullable=True)
    is_user_corrected = Column(Boolean, default=False, nullable=False)

    notes = Column(Text, nullable=True)
    source = Column(String(50), default="manual", nullable=False) # manual, csv_import, recurring_cron
    import_batch_id = Column(String(36), nullable=True)

    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index("idx_transaction_user_date", "user_id", "date"),
        Index("idx_transaction_user_category", "user_id", "category"),
    )
