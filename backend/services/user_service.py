"""User Management, Profile, Data Export and Deletion service."""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.core.security import hash_password, verify_password
from backend.core.exceptions import BadRequestException, UnauthorizedException, NotFoundException
from backend.models.user import User
from backend.models.transaction import Transaction, Category
from backend.models.budget import Budget
from backend.models.savings import SavingsGoal
from backend.models.debt import Debt
from backend.models.portfolio import Portfolio, PortfolioHolding
from backend.models.scenario import FinancialScenario
from backend.models.audit import AuditLog
from backend.schemas.user import UserUpdateRequest, PasswordChangeRequest, DataExportResponse


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: str) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User", user_id)
        return user

    def update_profile(self, user: User, payload: UserUpdateRequest) -> User:
        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.preferred_currency is not None:
            user.preferred_currency = payload.preferred_currency.upper()
        if payload.locale is not None:
            user.locale = payload.locale
        if payload.timezone is not None:
            user.timezone = payload.timezone
        if payload.theme is not None:
            user.theme = payload.theme
        if payload.monthly_income is not None:
            user.monthly_income = payload.monthly_income
        if payload.risk_tolerance is not None:
            user.risk_tolerance = payload.risk_tolerance
        if payload.custom_settings is not None:
            user.custom_settings = payload.custom_settings
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user: User, payload: PasswordChangeRequest) -> bool:
        if not verify_password(payload.current_password, user.hashed_password):
            raise UnauthorizedException("Current password does not match.")
        
        user.hashed_password = hash_password(payload.new_password)
        audit = AuditLog(
            user_id=user.id,
            action="password_change",
            status="success",
            details={}
        )
        self.db.add(audit)
        self.db.commit()
        return True

    def export_user_data(self, user: User) -> Dict[str, Any]:
        """Export all user-owned financial records for transparency and data portability."""
        txs = self.db.query(Transaction).filter(Transaction.user_id == user.id).all()
        budgets = self.db.query(Budget).filter(Budget.user_id == user.id).all()
        goals = self.db.query(SavingsGoal).filter(SavingsGoal.user_id == user.id).all()
        debts = self.db.query(Debt).filter(Debt.user_id == user.id).all()
        portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == user.id).all()
        scenarios = self.db.query(FinancialScenario).filter(FinancialScenario.user_id == user.id).all()

        export_payload = {
            "user_id": user.id,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "user_profile": {
                "email": user.email,
                "full_name": user.full_name,
                "preferred_currency": user.preferred_currency,
                "locale": user.locale,
                "timezone": user.timezone,
                "theme": user.theme,
                "monthly_income": user.monthly_income,
                "risk_tolerance": user.risk_tolerance,
                "created_at": user.created_at.isoformat()
            },
            "transactions": [
                {
                    "id": t.id,
                    "date": t.date.isoformat(),
                    "description": t.description,
                    "amount": float(t.amount),
                    "type": t.type,
                    "category": t.category,
                    "currency": t.currency,
                    "is_recurring": t.is_recurring,
                    "notes": t.notes
                }
                for t in txs
            ],
            "budgets": [
                {
                    "id": b.id,
                    "category": b.category,
                    "monthly_limit": float(b.monthly_limit),
                    "currency": b.currency,
                    "period": b.period
                }
                for b in budgets
            ],
            "savings_goals": [
                {
                    "id": g.id,
                    "title": g.title,
                    "target_amount": float(g.target_amount),
                    "current_amount": float(g.current_amount),
                    "target_date": g.target_date.isoformat(),
                    "monthly_contribution": float(g.monthly_contribution),
                    "status": g.status,
                    "priority": g.priority
                }
                for g in goals
            ],
            "debts": [
                {
                    "id": d.id,
                    "name": d.name,
                    "debt_type": d.debt_type,
                    "principal_amount": float(d.principal_amount),
                    "current_balance": float(d.current_balance),
                    "interest_rate_apr": float(d.interest_rate_apr),
                    "minimum_monthly_payment": float(d.minimum_monthly_payment)
                }
                for d in debts
            ],
            "portfolios": [
                {
                    "id": p.id,
                    "name": p.name,
                    "currency": p.currency,
                    "holdings": [
                        {
                            "symbol": h.symbol,
                            "name": h.name,
                            "asset_class": h.asset_class,
                            "quantity": float(h.quantity),
                            "average_buy_price": float(h.average_buy_price),
                            "current_price": float(h.current_price) if h.current_price else None
                        }
                        for h in p.holdings
                    ]
                }
                for p in portfolios
            ],
            "scenarios": [
                {
                    "id": s.id,
                    "title": s.title,
                    "scenario_type": s.scenario_type,
                    "input_parameters": s.input_parameters,
                    "output_results": s.output_results
                }
                for s in scenarios
            ]
        }

        audit = AuditLog(
            user_id=user.id,
            action="data_export",
            status="success",
            details={"record_count": len(txs) + len(budgets) + len(goals) + len(debts)}
        )
        self.db.add(audit)
        self.db.commit()

        return export_payload

    def delete_user_account(self, user: User, confirmation: str) -> bool:
        """Permanently delete user account and all cascaded data."""
        if confirmation != "DELETE_MY_ACCOUNT":
            raise BadRequestException("Confirmation string must be 'DELETE_MY_ACCOUNT'")
        
        user_id = user.id
        self.db.delete(user)
        self.db.commit()

        # Add unassociated system audit log for data deletion compliance
        system_audit = AuditLog(
            user_id=None,
            action="data_deletion_completed",
            status="success",
            details={"deleted_user_id": user_id}
        )
        self.db.add(system_audit)
        self.db.commit()
        return True
