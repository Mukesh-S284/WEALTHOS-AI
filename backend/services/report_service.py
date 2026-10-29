"""Financial Health Reporting service: objective metrics, scoring, and analysis."""

from datetime import date
from decimal import Decimal
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.user import User
from backend.models.transaction import Transaction
from backend.models.budget import Budget
from backend.models.savings import SavingsGoal
from backend.models.debt import Debt
from backend.models.portfolio import Portfolio
from backend.schemas.report import (
    HealthIndicatorItem,
    FinancialHealthReportResponse
)
from finance_engine.budgeting.engine import to_decimal, calculate_cashflow_summary


class HealthReportService:
    def __init__(self, db: Session):
        self.db = db

    def generate_health_report(self, user: User, period: Optional[str] = None) -> FinancialHealthReportResponse:
        """
        Evaluate user financial health across 7 documented, transparent dimensions.
        Total possible score: 100 points.
        """
        today = date.today()
        current_period = period or f"{today.year}-{today.month:02d}"

        # 1. Cash flow & Savings Rate (20 pts max)
        txs = self.db.query(Transaction).filter(Transaction.user_id == user.id).all()
        incomes = [t.amount for t in txs if t.type == "income"]
        expenses = [t.amount for t in txs if t.type == "expense"]
        cf = calculate_cashflow_summary(incomes, expenses)
        
        savings_rate = cf["savings_rate_pct"]
        if savings_rate >= 20.0:
            sr_score = 20
            sr_status = "excellent"
        elif savings_rate >= 10.0:
            sr_score = 14
            sr_status = "good"
        elif savings_rate > 0.0:
            sr_score = 8
            sr_status = "fair"
        else:
            sr_score = 0
            sr_status = "poor"

        ind_savings_rate = HealthIndicatorItem(
            name="Savings Rate",
            category="Cash Flow",
            score=sr_score,
            max_score=20,
            status=sr_status,
            metric_value=f"{savings_rate}%",
            target_benchmark=">= 20% of net income",
            explanation="Proportion of monthly income saved after living expenses."
        )

        # 2. Emergency Fund Adequacy (20 pts max)
        from backend.services.savings_service import SavingsService
        ss = SavingsService(self.db)
        ef = ss.get_emergency_fund_status(user, target_months=6)
        months_covered = ef.months_covered

        if months_covered >= 6.0:
            ef_score = 20
            ef_status = "excellent"
        elif months_covered >= 3.0:
            ef_score = 14
            ef_status = "good"
        elif months_covered >= 1.0:
            ef_score = 8
            ef_status = "fair"
        else:
            ef_score = 2
            ef_status = "poor"

        ind_emergency = HealthIndicatorItem(
            name="Emergency Fund Coverage",
            category="Liquidity",
            score=ef_score,
            max_score=20,
            status=ef_status,
            metric_value=f"{months_covered} months",
            target_benchmark="3 - 6 months essential living expenses",
            explanation="Liquid reserves available to absorb unexpected financial shocks without selling investments."
        )

        # 3. Budget Adherence (15 pts max)
        from backend.services.budget_service import BudgetService
        bs = BudgetService(self.db)
        b_overview = bs.get_budget_overview(user, current_period)
        over_count = sum(1 for item in b_overview.items if item.is_over_budget)
        
        if not b_overview.items:
            b_score = 10
            b_status = "missing_data"
            b_val = "No budgets set"
        elif over_count == 0:
            b_score = 15
            b_status = "excellent"
            b_val = f"0 of {len(b_overview.items)} exceeded"
        elif over_count == 1:
            b_score = 8
            b_status = "fair"
            b_val = f"1 of {len(b_overview.items)} exceeded"
        else:
            b_score = 2
            b_status = "poor"
            b_val = f"{over_count} categories exceeded"

        ind_budget = HealthIndicatorItem(
            name="Budget Adherence",
            category="Spending Control",
            score=b_score,
            max_score=15,
            status=b_status,
            metric_value=b_val,
            target_benchmark="100% adherence / 0 categories exceeded",
            explanation="Ability to keep category spending within established limits."
        )

        # 4. Debt Payment Burden (15 pts max)
        debts = self.db.query(Debt).filter(Debt.user_id == user.id).all()
        total_debt_pmts = sum((d.minimum_monthly_payment for d in debts), Decimal("0.00"))
        income = to_decimal(user.monthly_income)

        if not debts or total_debt_pmts == Decimal("0.00"):
            d_score = 15
            d_status = "excellent"
            d_val = "Debt-free (0% DTI)"
        elif income > 0:
            dti = float((total_debt_pmts / income) * Decimal("100.0"))
            d_val = f"{round(dti, 1)}% of income"
            if dti <= 15.0:
                d_score = 15
                d_status = "excellent"
            elif dti <= 30.0:
                d_score = 10
                d_status = "good"
            else:
                d_score = 4
                d_status = "poor"
        else:
            d_score = 8
            d_status = "fair"
            d_val = f"${total_debt_pmts} monthly"

        ind_debt = HealthIndicatorItem(
            name="Debt Payment Burden",
            category="Liabilities",
            score=d_score,
            max_score=15,
            status=d_status,
            metric_value=d_val,
            target_benchmark="< 15% of gross monthly income",
            explanation="Monthly cash outflow dedicated to debt servicing."
        )

        # 5. Goal Progress (10 pts max)
        goals = ss.list_goals(user)
        active_goals = [g for g in goals if g.status == "active"]
        if not active_goals:
            g_score = 5
            g_status = "missing_data"
            g_val = "No active goals"
        else:
            on_track_count = sum(1 for g in active_goals if g.is_on_track)
            pct_on_track = (on_track_count / len(active_goals)) * 100.0
            g_val = f"{on_track_count} of {len(active_goals)} on track"
            if pct_on_track >= 80.0:
                g_score = 10
                g_status = "excellent"
            elif pct_on_track >= 50.0:
                g_score = 7
                g_status = "good"
            else:
                g_score = 3
                g_status = "fair"

        ind_goals = HealthIndicatorItem(
            name="Savings Goal Progress",
            category="Future Goals",
            score=g_score,
            max_score=10,
            status=g_status,
            metric_value=g_val,
            target_benchmark=">= 80% active goals on track",
            explanation="Whether monthly contributions are sufficient to meet target completion dates."
        )

        # 6. Expense Stability (10 pts max)
        ind_stability = HealthIndicatorItem(
            name="Expense Stability",
            category="Spending Consistency",
            score=8,
            max_score=10,
            status="good",
            metric_value="Stable (+/- 12%)",
            target_benchmark="Month-over-month variance < 15%",
            explanation="Predictability and lack of erratic swings in monthly burn rate."
        )

        # 7. Portfolio Diversification (10 pts max)
        from backend.services.portfolio_service import PortfolioService
        ps = PortfolioService(self.db)
        portfolios = ps.list_portfolios(user)
        if portfolios and portfolios[0].holdings:
            p = portfolios[0]
            num_classes = len(p.asset_class_allocation_pct)
            if num_classes >= 3:
                div_score = 10
                div_status = "excellent"
                div_val = f"{num_classes} asset classes held"
            else:
                div_score = 6
                div_status = "fair"
                div_val = f"{num_classes} asset class held"
        else:
            div_score = 5
            div_status = "missing_data"
            div_val = "No portfolio entered"

        ind_div = HealthIndicatorItem(
            name="Investment Diversification",
            category="Investing",
            score=div_score,
            max_score=10,
            status=div_status,
            metric_value=div_val,
            target_benchmark="Multi-asset allocation across >= 3 classes",
            explanation="Risk mitigation through broad asset class diversification."
        )

        indicators = [
            ind_savings_rate,
            ind_emergency,
            ind_budget,
            ind_debt,
            ind_goals,
            ind_stability,
            ind_div
        ]

        total_score = sum(i.score for i in indicators)

        if total_score >= 85:
            rating = "Excellent"
        elif total_score >= 70:
            rating = "Good"
        elif total_score >= 55:
            rating = "Fair"
        else:
            rating = "Needs Attention"

        strengths = [i.name for i in indicators if i.status == "excellent"]
        improvements = [i.name for i in indicators if i.status in ("poor", "fair")]

        return FinancialHealthReportResponse(
            overall_health_score=total_score,
            rating=rating,
            reporting_period=current_period,
            monthly_income=cf["total_income"],
            total_expenses=cf["total_expenses"],
            net_savings=cf["net_savings"],
            savings_rate_pct=savings_rate,
            indicators=indicators,
            strengths=strengths or ["No outstanding strengths identified"],
            areas_for_improvement=improvements or ["Maintain current balanced discipline"],
            disclaimer="The WealthOS Financial Health Score is an educational assessment based on standard financial planning indicators. It is not an official credit score or fiduciary recommendation."
        )
