"""Debt management and payoff simulation service."""

from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.models.debt import Debt
from backend.models.user import User
from backend.schemas.debt import (
    DebtCreate,
    DebtUpdate,
    DebtResponse,
    DebtPayoffSimulationResponse,
    StrategyOutcome
)
from backend.core.exceptions import NotFoundException
from finance_engine.debt.engine import to_decimal, compare_debt_strategies


class DebtService:
    def __init__(self, db: Session):
        self.db = db

    def create_debt(self, user: User, payload: DebtCreate) -> Debt:
        debt = Debt(
            user_id=user.id,
            name=payload.name.strip(),
            debt_type=payload.debt_type,
            principal_amount=to_decimal(payload.principal_amount),
            current_balance=to_decimal(payload.current_balance),
            interest_rate_apr=to_decimal(payload.interest_rate_apr),
            minimum_monthly_payment=to_decimal(payload.minimum_monthly_payment),
            actual_monthly_payment=to_decimal(payload.actual_monthly_payment) if payload.actual_monthly_payment else None,
            currency=payload.currency.upper(),
            notes=payload.notes
        )
        self.db.add(debt)
        self.db.commit()
        self.db.refresh(debt)
        return debt

    def list_debts(self, user: User) -> List[Debt]:
        return self.db.query(Debt).filter(Debt.user_id == user.id).all()

    def get_debt(self, user: User, debt_id: str) -> Debt:
        d = self.db.query(Debt).filter(Debt.id == debt_id, Debt.user_id == user.id).first()
        if not d:
            raise NotFoundException("Debt", debt_id)
        return d

    def update_debt(self, user: User, debt_id: str, payload: DebtUpdate) -> Debt:
        d = self.get_debt(user, debt_id)
        if payload.name is not None:
            d.name = payload.name.strip()
        if payload.debt_type is not None:
            d.debt_type = payload.debt_type
        if payload.current_balance is not None:
            d.current_balance = to_decimal(payload.current_balance)
        if payload.interest_rate_apr is not None:
            d.interest_rate_apr = to_decimal(payload.interest_rate_apr)
        if payload.minimum_monthly_payment is not None:
            d.minimum_monthly_payment = to_decimal(payload.minimum_monthly_payment)
        if payload.actual_monthly_payment is not None:
            d.actual_monthly_payment = to_decimal(payload.actual_monthly_payment)
        if payload.notes is not None:
            d.notes = payload.notes
        self.db.commit()
        self.db.refresh(d)
        return d

    def delete_debt(self, user: User, debt_id: str) -> bool:
        d = self.get_debt(user, debt_id)
        self.db.delete(d)
        self.db.commit()
        return True

    def simulate_payoff(self, user: User, extra_payment: Decimal = Decimal("0.00")) -> DebtPayoffSimulationResponse:
        debts = self.list_debts(user)
        debt_dicts = [
            {
                "name": d.name,
                "balance": d.current_balance,
                "apr": d.interest_rate_apr,
                "min_payment": d.minimum_monthly_payment
            }
            for d in debts
        ]
        
        comparison = compare_debt_strategies(debt_dicts, extra_monthly_payment=extra_payment)
        av = comparison["avalanche"]
        sn = comparison["snowball"]

        return DebtPayoffSimulationResponse(
            avalanche=StrategyOutcome(
                strategy=av["strategy"],
                total_months=av["total_months"],
                total_interest_paid=av["total_interest_paid"],
                total_principal_paid=av["total_principal_paid"],
                total_paid=av["total_paid"],
                debts_payoff_order=av["debts_payoff_order"]
            ),
            snowball=StrategyOutcome(
                strategy=sn["strategy"],
                total_months=sn["total_months"],
                total_interest_paid=sn["total_interest_paid"],
                total_principal_paid=sn["total_principal_paid"],
                total_paid=sn["total_paid"],
                debts_payoff_order=sn["debts_payoff_order"]
            ),
            avalanche_interest_savings=comparison["avalanche_interest_savings"],
            avalanche_months_saved=comparison["avalanche_months_saved"],
            recommendation=comparison["recommendation"]
        )
