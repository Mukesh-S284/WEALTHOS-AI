"""Purchase Affordability Evaluation service."""

from decimal import Decimal
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.user import User
from backend.models.savings import SavingsGoal
from backend.models.debt import Debt
from backend.models.transaction import Transaction
from backend.schemas.purchase import PurchaseEvaluationRequest, PurchaseEvaluationResponse
from finance_engine.purchases.engine import evaluate_purchase_decision, to_decimal


class PurchaseService:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_purchase(
        self,
        user: User,
        payload: PurchaseEvaluationRequest
    ) -> PurchaseEvaluationResponse:
        """
        Evaluate purchase affordability using user's real financial context
        (savings balances, income surplus, debt obligations, essential buffer)
        with overrides if specified in request.
        """
        # 1. Determine Available Liquid Savings
        if payload.available_liquid_savings is not None:
            savings = to_decimal(payload.available_liquid_savings)
        else:
            total_savings = self.db.query(func.sum(SavingsGoal.current_amount)).filter(
                SavingsGoal.user_id == user.id
            ).scalar()
            savings = to_decimal(total_savings) if total_savings else Decimal("1000.00")

        # 2. Determine Monthly Net Surplus
        if payload.monthly_net_surplus is not None:
            surplus = to_decimal(payload.monthly_net_surplus)
        else:
            monthly_income = to_decimal(user.monthly_income)
            # Total monthly debt obligations
            total_debt_pmts = self.db.query(func.sum(Debt.minimum_monthly_payment)).filter(
                Debt.user_id == user.id
            ).scalar()
            debt_min = to_decimal(total_debt_pmts) if total_debt_pmts else Decimal("0.00")
            
            # Monthly savings commitments
            monthly_savings = self.db.query(func.sum(SavingsGoal.monthly_contribution)).filter(
                SavingsGoal.user_id == user.id,
                SavingsGoal.status == "active"
            ).scalar()
            savings_commitments = to_decimal(monthly_savings) if monthly_savings else Decimal("0.00")

            # Standard assumed surplus: income - (living expenses 50% + debt + goals)
            living_exp = monthly_income * Decimal("0.50")
            surplus = max(Decimal("0.00"), monthly_income - living_exp - debt_min - savings_commitments)

        # 3. Determine Minimum Cash Buffer
        if payload.minimum_cash_buffer is not None:
            buffer = to_decimal(payload.minimum_cash_buffer)
        else:
            # 3 months buffer based on 50% income living expense
            income = to_decimal(user.monthly_income)
            buffer = (income * Decimal("0.50") * Decimal("3.0")).quantize(Decimal("0.01")) if income > 0 else Decimal("3000.00")

        results = evaluate_purchase_decision(
            purchase_price=payload.purchase_price,
            available_liquid_savings=savings,
            monthly_net_surplus=surplus,
            minimum_cash_buffer=buffer,
            financing_apr=payload.financing_apr,
            financing_tenure_months=payload.financing_tenure_months,
            alternative_price=payload.alternative_price
        )

        return PurchaseEvaluationResponse(
            purchase_price=results["purchase_price"],
            available_liquid_savings=results["available_liquid_savings"],
            monthly_net_surplus=results["monthly_net_surplus"],
            minimum_cash_buffer=results["minimum_cash_buffer"],
            verdict=results["verdict"],
            verdict_summary=results["verdict_summary"],
            scenarios=results["scenarios"]
        )
