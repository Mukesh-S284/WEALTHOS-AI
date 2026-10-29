"""AI Assistant Session and Message database models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON, Index
from sqlalchemy.orm import relationship
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class AssistantSession(Base):
    __tablename__ = "assistant_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(150), default="New Financial Conversation", nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="assistant_sessions")
    messages = relationship("AssistantMessage", back_populates="session", cascade="all, delete-orphan", order_by="AssistantMessage.created_at")

    __table_args__ = (
        Index("idx_session_user", "user_id"),
    )


class AssistantMessage(Base):
    __tablename__ = "assistant_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("assistant_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(String(20), nullable=False) # user, assistant, system, tool
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True) # list of tool execution payloads
    tool_results = Column(JSON, nullable=True) # tool execution results
    citations = Column(JSON, nullable=True) # sources cited
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    session = relationship("AssistantSession", back_populates="messages")
