"""Unified Financial Decision Engine service: Cross-module impact and scenario analysis."""

from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.models.transaction import Transaction
from backend.models.debt import Debt
from backend.models.savings import SavingsGoal
from backend.models.portfolio import Portfolio
from backend.schemas.unified_decision import (
    DecisionEvaluationRequest,
    UnifiedDecisionEvaluationResponse,
    CrossGoalImpact,
    EmergencyFundImpact,
    BudgetImpact,
    DebtImpact,
    UnifiedDashboardOverviewResponse
)
from backend.core.exceptions import BadRequestException
from finance_engine.budgeting.engine import to_decimal, calculate_cashflow_summary
from finance_engine.purchases.engine import calculate_loan_payment
from backend.services.savings_service import SavingsService
from backend.services.report_service import HealthReportService
from backend.services.portfolio_service import PortfolioService


class UnifiedDecisionService:
    def __init__(self, db: Session):
        self.db = db
        self.savings_service = SavingsService(db)
        self.report_service = HealthReportService(db)
        self.portfolio_service = PortfolioService(db)

    def get_dashboard_overview(self, user: User) -> UnifiedDashboardOverviewResponse:
        """Aggregate real-time financial health snapshot across all active modules."""
        txs = self.db.query(Transaction).filter(Transaction.user_id == user.id).all()
        incomes = [t.amount for t in txs if t.type == "income"]
        expenses = [t.amount for t in txs if t.type == "expense"]
        cf = calculate_cashflow_summary(incomes, expenses)

        # Baseline income from user profile if no transactions
        inc = cf["total_income"] or to_decimal(user.monthly_income)
        exp = cf["total_expenses"]
        surplus = inc - exp
        savings_rate = float((surplus / inc) * Decimal("100.0")) if inc > Decimal("0.00") else 0.0
        savings_rate = max(0.0, savings_rate)

        # Emergency fund
        ef = self.savings_service.get_emergency_fund_status(user, target_months=6)

        # Debts
        debts = self.db.query(Debt).filter(Debt.user_id == user.id).all()
        total_debt = sum((d.current_balance for d in debts), Decimal("0.00"))
        monthly_debt_pmts = sum((d.minimum_monthly_payment for d in debts), Decimal("0.00"))
        dti = float((monthly_debt_pmts / inc) * Decimal("100.0")) if inc > Decimal("0.00") else 0.0

        # Portfolio
        portfolios = self.portfolio_service.list_portfolios(user)
        total_p_val = sum((p.total_value for p in portfolios), Decimal("0.00"))

        # Goals
        goals = self.savings_service.list_goals(user)
        active_goals = [g for g in goals if g.status == "active"]

        # Health score
        health_rep = self.report_service.generate_health_report(user)

        return UnifiedDashboardOverviewResponse(
            user_id=user.id,
            currency=user.preferred_currency or "USD",
            monthly_income=inc,
            monthly_expenses=exp,
            net_monthly_savings=surplus,
            savings_rate_pct=round(savings_rate, 2),
            emergency_fund_months=ef.months_covered,
            total_debt_balance=total_debt,
            debt_to_income_pct=round(dti, 2),
            total_portfolio_value=total_p_val,
            active_goals_count=len(active_goals),
            health_score=health_rep.overall_health_score,
            health_rating=health_rep.rating
        )

    def evaluate_decision(self, user: User, req: DecisionEvaluationRequest) -> UnifiedDecisionEvaluationResponse:
        """
        Evaluate hypothetical financial decisions across all 4 pillars:
        1. Budget Surplus
        2. Emergency Reserves
        3. Debt Burden (DTI)
        4. Savings Goal Delays
        """
        overview = self.get_dashboard_overview(user)
        debts = self.db.query(Debt).filter(Debt.user_id == user.id).all()
        monthly_debt_before = sum((d.minimum_monthly_payment for d in debts), Decimal("0.00"))
        inc = overview.monthly_income
        exp_before = overview.monthly_expenses
        surplus_before = overview.net_monthly_savings
        dti_before = overview.debt_to_income_pct
        ef_months_before = overview.emergency_fund_months

        active_goals = self.savings_service.list_goals(user)
        total_goal_contribs = sum((g.monthly_contribution for g in active_goals), Decimal("0.00"))

        tradeoffs: List[str] = []
        alternatives: List[str] = []
        goal_impacts: List[CrossGoalImpact] = []

        if req.decision_type == "expensive_purchase":
            if not req.purchase:
                raise BadRequestException("Purchase details required for 'expensive_purchase' decision type.")
            p = req.purchase

            if p.financing_option == "cash":
                # Paid from liquid cash
                purchase_cost = p.cost
                # Estimate monthly living expenses
                monthly_living = exp_before if exp_before > Decimal("0.00") else Decimal("2000.00")
                liquid_reserves_before = ef_months_before * float(monthly_living)
                liquid_reserves_after = max(0.0, liquid_reserves_before - float(purchase_cost))
                ef_months_after = round(liquid_reserves_after / float(monthly_living), 2)
                months_depleted = round(max(0.0, ef_months_before - ef_months_after), 2)
                
                exp_after = exp_before
                surplus_after = surplus_before
                debt_after = monthly_debt_before
                dti_after = dti_before

                # Buffer rebuild calculation
                rebuild_months = None
                if months_depleted > 0 and surplus_after > Decimal("0.00"):
                    cash_needed = Decimal(str(liquid_reserves_before - liquid_reserves_after))
                    rebuild_months = int((cash_needed / surplus_after).to_integral_value()) + 1

                tradeoffs.append(f"Paying ${purchase_cost:,.2f} in cash reduces liquid buffer by {months_depleted} months of expenses.")
                if rebuild_months:
                    tradeoffs.append(f"At current monthly surplus (${surplus_after:,.2f}), replenishing this reserve will require {rebuild_months} months.")

            else:
                # Financed purchase
                down = p.down_payment or Decimal("0.00")
                loan_principal = max(Decimal("0.00"), p.cost - down)
                loan_calc = calculate_loan_payment(
                    principal=loan_principal,
                    annual_interest_rate_pct=p.loan_interest_rate_pct or Decimal("7.0"),
                    tenure_months=p.loan_term_months or 36
                )
                monthly_pmt = loan_calc["monthly_payment"]
                exp_after = exp_before + monthly_pmt
                surplus_after = inc - exp_after
                debt_after = monthly_debt_before + monthly_pmt
                dti_after = float((debt_after / inc) * Decimal("100.0")) if inc > Decimal("0.00") else 0.0

                ef_months_after = ef_months_before
                months_depleted = 0.0
                rebuild_months = None

                tradeoffs.append(f"Financing requires an ongoing monthly commitment of ${monthly_pmt:,.2f} for {p.loan_term_months or 36} months.")
                tradeoffs.append(f"Total debt-to-income ratio increases from {dti_before:.1f}% to {dti_after:.1f}%.")

                # Cross-goal delay evaluation
                if surplus_after < total_goal_contribs:
                    shortfall = total_goal_contribs - max(Decimal("0.00"), surplus_after)
                    tradeoffs.append(
                        f"Monthly surplus of ${surplus_after:,.2f} is insufficient to fund all active savings goal contributions (${total_goal_contribs:,.2f}), creating a monthly gap of ${shortfall:,.2f}."
                    )
                    # Distribute delay across goals
                    for g in active_goals:
                        if g.monthly_contribution > Decimal("0.00"):
                            reduction_share = (g.monthly_contribution / total_goal_contribs) * shortfall
                            new_contrib = max(Decimal("0.00"), g.monthly_contribution - reduction_share)
                            remaining_amount = max(Decimal("0.00"), g.target_amount - g.current_amount)
                            
                            delay = 0
                            if new_contrib > Decimal("0.00"):
                                orig_months = int(remaining_amount / g.monthly_contribution)
                                new_months = int(remaining_amount / new_contrib)
                                delay = max(0, new_months - orig_months)
                            else:
                                delay = 999

                            goal_impacts.append(
                                CrossGoalImpact(
                                    goal_id=g.id,
                                    goal_title=g.title,
                                    target_amount=g.target_amount,
                                    current_amount=g.current_amount,
                                    current_monthly_contribution=g.monthly_contribution,
                                    new_monthly_contribution=new_contrib,
                                    projected_delay_months=delay,
                                    impact_summary=f"Contribution reduced by ${reduction_share:,.2f}/mo, delaying completion by approx {delay} months."
                                )
                            )

            # Recommendations & Alternatives
            if surplus_after < Decimal("0.00") or ef_months_after < 1.0 or dti_after > 45.0:
                verdict = "NOT_RECOMMENDED"
                is_rec = False
                summary = "This purchase severely strains your financial foundation, resulting in negative monthly cash flow, depleted liquidity, or excessive debt leverage."
                alternatives.append("Delay purchase until 6 months of living expenses are securely saved.")
                alternatives.append("Explore certified pre-owned or secondary market options to lower the cost by 30-50%.")
                alternatives.append("Increase down payment to reduce monthly debt service.")
            elif ef_months_after < 3.0 or dti_after > 36.0 or surplus_after < (total_goal_contribs * Decimal("0.5")):
                verdict = "PROCEED_WITH_CAUTION"
                is_rec = True
                summary = "Purchase is technically feasible but tightens your financial margin of safety, extending savings goal deadlines or lowering your emergency buffer."
                alternatives.append("Negotiate loan APR or shop with credit unions for lower financing rates.")
                alternatives.append("Pause discretionary want categories temporarily during the first 6 months of financing.")
            else:
                verdict = "APPROVED_SAFE"
                is_rec = True
                summary = "Purchase fits comfortably within your financial parameters. Cash flow remains positive and emergency liquidity remains resilient."
                alternatives.append("Set up automated autopay to maintain spotless payment history.")

        elif req.decision_type == "increase_savings_sip":
            sip_add = req.additional_sip_amount or Decimal("200.00")
            exp_after = exp_before
            surplus_after = surplus_before - sip_add
            debt_after = monthly_debt_before
            dti_after = dti_before
            ef_months_after = ef_months_before
            months_depleted = 0.0
            rebuild_months = None

            if surplus_after >= Decimal("0.00"):
                verdict = "APPROVED_SAFE"
                is_rec = True
                summary = f"Increasing automated monthly investment by ${sip_add:,.2f} is well within your surplus (${surplus_before:,.2f}) and accelerates long-term compound growth."
                tradeoffs.append(f"Remaining discretionary unallocated surplus is ${surplus_after:,.2f}/month.")
            else:
                verdict = "NOT_RECOMMENDED"
                is_rec = False
                summary = f"Proposed monthly SIP increase (${sip_add:,.2f}) exceeds current monthly surplus (${surplus_before:,.2f}), which would induce cash flow deficit."
                alternatives.append(f"Cap additional monthly SIP to ${max(Decimal('0.00'), surplus_before):,.2f}.")

        elif req.decision_type == "extra_debt_payment":
            extra_pmt = req.extra_debt_payment_monthly or Decimal("100.00")
            exp_after = exp_before + extra_pmt
            surplus_after = surplus_before - extra_pmt
            debt_after = monthly_debt_before + extra_pmt
            dti_after = float((debt_after / inc) * Decimal("100.0")) if inc > Decimal("0.00") else 0.0
            ef_months_after = ef_months_before
            months_depleted = 0.0
            rebuild_months = None

            if surplus_after >= Decimal("0.00"):
                verdict = "APPROVED_SAFE"
                is_rec = True
                summary = f"Accelerating debt repayment with an extra ${extra_pmt:,.2f}/month saves interest and clears high-cost liabilities faster."
                tradeoffs.append(f"Directs ${extra_pmt:,.2f}/month away from other goals toward debt principal.")
            else:
                verdict = "PROCEED_WITH_CAUTION"
                is_rec = False
                summary = f"Extra debt payment of ${extra_pmt:,.2f} triggers negative monthly cash flow. Scale back to avoid missing other obligations."
                alternatives.append(f"Allocate an extra ${max(Decimal('0.00'), surplus_before):,.2f}/month instead.")

        else:
            raise BadRequestException(f"Unsupported decision_type: '{req.decision_type}'")

        # Health score delta projection
        score_before = overview.health_score
        score_delta = 0
        if verdict == "APPROVED_SAFE":
            score_delta = 3 if req.decision_type in ("increase_savings_sip", "extra_debt_payment") else 0
        elif verdict == "PROCEED_WITH_CAUTION":
            score_delta = -8
        else:
            score_delta = -20
        score_after = max(0, min(100, score_before + score_delta))

        return UnifiedDecisionEvaluationResponse(
            decision_type=req.decision_type,
            is_recommended=is_rec,
            recommendation_verdict=verdict,
            executive_summary=summary,
            budget_impact=BudgetImpact(
                monthly_income=inc,
                monthly_expenses_before=exp_before,
                monthly_expenses_after=exp_after,
                monthly_surplus_before=surplus_before,
                monthly_surplus_after=surplus_after,
                surplus_change=surplus_after - surplus_before,
                is_cashflow_negative=bool(surplus_after < Decimal("0.00"))
            ),
            emergency_fund_impact=EmergencyFundImpact(
                months_before=ef_months_before,
                months_after=ef_months_after,
                months_depleted=months_depleted,
                rebuild_months=rebuild_months,
                is_compromised=bool(ef_months_after < 3.0)
            ),
            debt_impact=DebtImpact(
                dti_pct_before=dti_before,
                dti_pct_after=dti_after,
                total_monthly_debt_service_before=monthly_debt_before,
                total_monthly_debt_service_after=debt_after,
                is_dti_high_risk=bool(dti_after > 36.0)
            ),
            cross_goal_impacts=goal_impacts,
            tradeoff_analysis=tradeoffs,
            actionable_alternatives=alternatives,
            health_score_before=score_before,
            estimated_health_score_after=score_after,
            disclaimer="The Unified Financial Decision Engine provides deterministic scenario modeling based on user data. It does not provide personalized legal, tax, or investment advice."
        )
