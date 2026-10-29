"""Security and Activity Audit Log database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, Index
from sqlalchemy.orm import relationship
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    action = Column(String(50), nullable=False, index=True) # login, register, data_export, data_deletion, etc.
    status = Column(String(20), default="success", nullable=False) # success, failure, denied
    ip_address = Column(String(45), nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    
    timestamp = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)

    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_user_action_time", "user_id", "action", "timestamp"),
    )
