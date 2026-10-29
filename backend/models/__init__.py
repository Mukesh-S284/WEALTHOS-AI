"""SQLAlchemy database models package."""

from backend.core.database import Base
from backend.models.user import User
from backend.models.transaction import Transaction, Category
from backend.models.budget import Budget
from backend.models.savings import SavingsGoal, SavingsContribution
from backend.models.debt import Debt
from backend.models.portfolio import Portfolio, PortfolioHolding
from backend.models.market import SupportedInstrument, MarketObservation
from backend.models.scenario import FinancialScenario
from backend.models.learning import LearningProgress
from backend.models.knowledge import KnowledgeDocument, KnowledgeChunk
from backend.models.assistant import AssistantSession, AssistantMessage
from backend.models.audit import AuditLog

__all__ = [
    "Base",
    "User",
    "Transaction",
    "Category",
    "Budget",
    "SavingsGoal",
    "SavingsContribution",
    "Debt",
    "Portfolio",
    "PortfolioHolding",
    "SupportedInstrument",
    "MarketObservation",
    "FinancialScenario",
    "LearningProgress",
    "KnowledgeDocument",
    "KnowledgeChunk",
    "AssistantSession",
    "AssistantMessage",
    "AuditLog"
]
