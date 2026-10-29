"""Financial Learning and Quiz database models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Boolean, JSON, Index
from sqlalchemy.orm import relationship
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    topic_id = Column(String(50), nullable=False) # budgeting, sips, emergency_funds, bonds, crypto_risks, etc.
    completed = Column(Boolean, default=False, nullable=False)
    quiz_score = Column(Integer, nullable=True) # Percentage (0-100)
    quiz_attempts = Column(Integer, default=0, nullable=False)
    last_studied_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    notes = Column(JSON, default=dict, nullable=False)

    user = relationship("User", back_populates="learning_progress")

    __table_args__ = (
        Index("idx_learning_user_topic", "user_id", "topic_id", unique=True),
    )
