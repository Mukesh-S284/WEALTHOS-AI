"""Savings Goal and Emergency Fund management service."""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.savings import SavingsGoal, SavingsContribution
from backend.models.transaction import Transaction
from backend.models.user import User
from backend.schemas.savings import (
    SavingsGoalCreate,
    SavingsGoalUpdate,
    SavingsGoalResponse,
    SavingsContributionCreate,
    EmergencyFundResponse
)
from backend.core.exceptions import NotFoundException, BadRequestException
from finance_engine.savings.engine import (
    to_decimal,
    calculate_required_monthly_savings,
    calculate_projected_completion_date,
    calculate_emergency_fund_status
)


class SavingsService:
    def __init__(self, db: Session):
        self.db = db

    def _enrich_goal(self, goal: SavingsGoal) -> SavingsGoalResponse:
        """Calculate dynamic metrics for a goal."""
        req_calc = calculate_required_monthly_savings(
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            target_date=goal.target_date,
            annual_return_pct=goal.expected_annual_return_pct
        )
        
        proj_calc = calculate_projected_completion_date(
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            monthly_contribution=goal.monthly_contribution,
            annual_return_pct=goal.expected_annual_return_pct
        )

        is_on_track = bool(
            goal.current_amount >= goal.target_amount or
            (goal.monthly_contribution >= req_calc["required_monthly_contribution"] and not req_calc["is_overdue"])
        )

        return SavingsGoalResponse(
            id=goal.id,
            user_id=goal.user_id,
            title=goal.title,
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            target_date=goal.target_date,
            monthly_contribution=goal.monthly_contribution,
            priority=goal.priority,
            status=goal.status,
            category=goal.category,
            expected_annual_return_pct=goal.expected_annual_return_pct,
            currency=goal.currency,
            notes=goal.notes,
            required_monthly_savings=req_calc["required_monthly_contribution"],
            projected_completion_date=proj_calc.get("projected_date"),
            is_on_track=is_on_track,
            created_at=goal.created_at,
            updated_at=goal.updated_at
        )

    def create_goal(self, user: User, payload: SavingsGoalCreate) -> SavingsGoalResponse:
        goal = SavingsGoal(
            user_id=user.id,
            title=payload.title.strip(),
            target_amount=to_decimal(payload.target_amount),
            current_amount=to_decimal(payload.current_amount),
            target_date=payload.target_date,
            monthly_contribution=to_decimal(payload.monthly_contribution),
            priority=payload.priority,
            status="active",
            category=payload.category,
            expected_annual_return_pct=to_decimal(payload.expected_annual_return_pct),
            currency=payload.currency.upper(),
            notes=payload.notes
        )
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return self._enrich_goal(goal)

    def list_goals(self, user: User, status: Optional[str] = None) -> List[SavingsGoalResponse]:
        query = self.db.query(SavingsGoal).filter(SavingsGoal.user_id == user.id)
        if status:
            query = query.filter(SavingsGoal.status == status.lower())
        goals = query.order_by(SavingsGoal.target_date.asc()).all()
        return [self._enrich_goal(g) for g in goals]

    def get_goal(self, user: User, goal_id: str) -> SavingsGoalResponse:
        g = self.db.query(SavingsGoal).filter(
            SavingsGoal.id == goal_id,
            SavingsGoal.user_id == user.id
        ).first()
        if not g:
            raise NotFoundException("SavingsGoal", goal_id)
        return self._enrich_goal(g)

    def update_goal(self, user: User, goal_id: str, payload: SavingsGoalUpdate) -> SavingsGoalResponse:
        g = self.db.query(SavingsGoal).filter(
            SavingsGoal.id == goal_id,
            SavingsGoal.user_id == user.id
        ).first()
        if not g:
            raise NotFoundException("SavingsGoal", goal_id)

        if payload.title is not None:
            g.title = payload.title.strip()
        if payload.target_amount is not None:
            g.target_amount = to_decimal(payload.target_amount)
        if payload.current_amount is not None:
            g.current_amount = to_decimal(payload.current_amount)
        if payload.target_date is not None:
            g.target_date = payload.target_date
        if payload.monthly_contribution is not None:
            g.monthly_contribution = to_decimal(payload.monthly_contribution)
        if payload.priority is not None:
            g.priority = payload.priority
        if payload.status is not None:
            g.status = payload.status.lower()
        if payload.category is not None:
            g.category = payload.category
        if payload.expected_annual_return_pct is not None:
            g.expected_annual_return_pct = to_decimal(payload.expected_annual_return_pct)
        if payload.notes is not None:
            g.notes = payload.notes

        self.db.commit()
        self.db.refresh(g)
        return self._enrich_goal(g)

    def delete_goal(self, user: User, goal_id: str) -> bool:
        g = self.db.query(SavingsGoal).filter(
            SavingsGoal.id == goal_id,
            SavingsGoal.user_id == user.id
        ).first()
        if not g:
            raise NotFoundException("SavingsGoal", goal_id)
        self.db.delete(g)
        self.db.commit()
        return True

    def add_contribution(
        self,
        user: User,
        goal_id: str,
        payload: SavingsContributionCreate
    ) -> SavingsGoalResponse:
        g = self.db.query(SavingsGoal).filter(
            SavingsGoal.id == goal_id,
            SavingsGoal.user_id == user.id
        ).first()
        if not g:
            raise NotFoundException("SavingsGoal", goal_id)

        contrib = SavingsContribution(
            goal_id=g.id,
            user_id=user.id,
            amount=to_decimal(payload.amount),
            date=payload.date or date.today(),
            notes=payload.notes
        )
        self.db.add(contrib)
        g.current_amount += to_decimal(payload.amount)
        if g.current_amount >= g.target_amount:
            g.status = "completed"

        self.db.commit()
        self.db.refresh(g)
        return self._enrich_goal(g)

    def get_emergency_fund_status(self, user: User, target_months: int = 6) -> EmergencyFundResponse:
        """Calculate emergency fund progress based on actual user transactions and emergency goal."""
        # 1. Total savings allocated to emergency fund goals
        emergency_goal = self.db.query(SavingsGoal).filter(
            SavingsGoal.user_id == user.id,
            SavingsGoal.category == "emergency_fund"
        ).first()
        
        current_savings = emergency_goal.current_amount if emergency_goal else Decimal("0.00")

        # 2. Compute essential monthly expenses from transaction history
        # (Housing, Utilities, Groceries, Healthcare)
        essential_categories = ["Housing", "Utilities", "Groceries", "Healthcare"]
        recent_essential = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == "expense",
            Transaction.category.in_(essential_categories)
        ).scalar()

        if recent_essential and recent_essential > 0:
            monthly_essential = to_decimal(recent_essential)
        else:
            # Fallback based on declared monthly income: 50% rule for essentials
            income = to_decimal(user.monthly_income)
            monthly_essential = (income * Decimal("0.50")).quantize(Decimal("0.01")) if income > 0 else Decimal("2000.00")

        calc = calculate_emergency_fund_status(
            current_savings=current_savings,
            monthly_essential_expenses=monthly_essential,
            target_months=target_months
        )

        return EmergencyFundResponse(
            target_months=calc["target_months"],
            monthly_essential_expenses=calc["monthly_essential_expenses"],
            target_amount=calc["target_amount"],
            current_savings=calc["current_savings"],
            months_covered=calc["months_covered"],
            gap_amount=calc["gap_amount"],
            health_status=calc["health_status"]
        )
