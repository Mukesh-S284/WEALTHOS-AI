"""Budget management and status calculation service."""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract

from backend.models.budget import Budget
from backend.models.transaction import Transaction
from backend.models.user import User
from backend.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetStatusItem,
    BudgetOverviewResponse
)
from backend.core.exceptions import NotFoundException, ConflictException, BadRequestException
from finance_engine.budgeting.engine import calculate_budget_status, to_decimal


class BudgetService:
    def __init__(self, db: Session):
        self.db = db

    def set_budget(self, user: User, payload: BudgetCreate) -> Budget:
        """Create or update monthly budget for a category and period."""
        existing = self.db.query(Budget).filter(
            Budget.user_id == user.id,
            Budget.category == payload.category.strip(),
            Budget.period == payload.period.strip()
        ).first()

        if existing:
            existing.monthly_limit = to_decimal(payload.monthly_limit)
            existing.alert_threshold_percentage = to_decimal(payload.alert_threshold_percentage)
            existing.currency = payload.currency.upper()
            self.db.commit()
            self.db.refresh(existing)
            return existing

        budget = Budget(
            user_id=user.id,
            category=payload.category.strip(),
            monthly_limit=to_decimal(payload.monthly_limit),
            currency=payload.currency.upper(),
            period=payload.period.strip(),
            alert_threshold_percentage=to_decimal(payload.alert_threshold_percentage)
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def get_budget(self, user: User, budget_id: str) -> Budget:
        b = self.db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user.id
        ).first()
        if not b:
            raise NotFoundException("Budget", budget_id)
        return b

    def update_budget(self, user: User, budget_id: str, payload: BudgetUpdate) -> Budget:
        b = self.get_budget(user, budget_id)
        if payload.monthly_limit is not None:
            b.monthly_limit = to_decimal(payload.monthly_limit)
        if payload.alert_threshold_percentage is not None:
            b.alert_threshold_percentage = to_decimal(payload.alert_threshold_percentage)
        self.db.commit()
        self.db.refresh(b)
        return b

    def delete_budget(self, user: User, budget_id: str) -> bool:
        b = self.get_budget(user, budget_id)
        self.db.delete(b)
        self.db.commit()
        return True

    def get_budget_overview(self, user: User, period: str) -> BudgetOverviewResponse:
        """
        Evaluate actual monthly spending against user budget limits for the period.
        Period format: 'YYYY-MM' e.g. '2026-10'
        """
        # Fetch user budgets for this period or recurring 'ALL'
        budgets = self.db.query(Budget).filter(
            Budget.user_id == user.id,
            Budget.period.in_([period, "ALL"])
        ).all()

        # Parse year and month
        try:
            year_str, month_str = period.split("-")
            year = int(year_str)
            month = int(month_str)
        except ValueError:
            raise BadRequestException("Period must be formatted as 'YYYY-MM' (e.g. '2026-10')")

        # Query actual spending grouped by category for this period
        spending_records = self.db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total_spent")
        ).filter(
            Transaction.user_id == user.id,
            Transaction.type == "expense",
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month
        ).group_by(Transaction.category).all()

        spent_map = {rec.category: to_decimal(rec.total_spent) for rec in spending_records}

        items: List[BudgetStatusItem] = []
        total_budgeted = Decimal("0.00")
        total_spent = Decimal("0.00")

        for b in budgets:
            category_spent = spent_map.get(b.category, Decimal("0.00"))
            status = calculate_budget_status(
                monthly_limit=b.monthly_limit,
                total_spent=category_spent,
                alert_threshold_pct=b.alert_threshold_percentage
            )
            total_budgeted += b.monthly_limit
            total_spent += category_spent

            items.append(
                BudgetStatusItem(
                    budget_id=b.id,
                    category=b.category,
                    monthly_limit=b.monthly_limit,
                    spent_amount=status["spent_amount"],
                    remaining_amount=status["remaining_amount"],
                    percentage_used=status["percentage_used"],
                    is_over_budget=status["is_over_budget"],
                    is_near_limit=status["is_near_limit"],
                    currency=b.currency,
                    period=period
                )
            )

        total_remaining = total_budgeted - total_spent
        overall_pct = float((total_spent / total_budgeted * Decimal("100.0"))) if total_budgeted > 0 else 0.0

        return BudgetOverviewResponse(
            period=period,
            currency=user.preferred_currency,
            total_budgeted=total_budgeted,
            total_spent=total_spent,
            total_remaining=total_remaining,
            overall_percentage_used=round(overall_pct, 2),
            items=items
        )
