"""Financial Scenario database models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON, Index
from sqlalchemy.orm import relationship
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class FinancialScenario(Base):
    __tablename__ = "financial_scenarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(150), nullable=False)
    scenario_type = Column(String(50), nullable=False) # purchase_decision, life_event, future_wealth, debt_payoff
    description = Column(Text, nullable=True)
    
    input_parameters = Column(JSON, default=dict, nullable=False)
    output_results = Column(JSON, default=dict, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="scenarios")

    __table_args__ = (
        Index("idx_scenario_user_type", "user_id", "scenario_type"),
    )
