"""Unit tests for Debt Avalanche vs Snowball repayment strategies."""

from decimal import Decimal
from finance_engine.debt.engine import simulate_debt_payoff, compare_debt_strategies


def test_avalanche_vs_snowball_simulation():
    # Two debts:
    # 1. Credit Card: $5,000 at 22% APR, min $150
    # 2. Student Loan: $1,500 at 6% APR, min $50
    debts = [
        {"name": "Credit Card", "balance": Decimal("5000.00"), "apr": Decimal("22.0"), "min_payment": Decimal("150.00")},
        {"name": "Student Loan", "balance": Decimal("1500.00"), "apr": Decimal("6.0"), "min_payment": Decimal("50.00")}
    ]

    res = compare_debt_strategies(debts, extra_monthly_payment=Decimal("100.00"))

    avalanche = res["avalanche"]
    snowball = res["snowball"]

    # Avalanche prioritizes the 22% debt, so its total interest paid MUST be <= Snowball
    assert avalanche["total_interest_paid"] <= snowball["total_interest_paid"]
    # Snowball must pay off the smaller debt first
    assert snowball["debts_payoff_order"][0]["name"] == "Student Loan"
    # Avalanche must pay off the higher APR debt first
    assert avalanche["debts_payoff_order"][0]["name"] == "Credit Card"
    assert res["avalanche_interest_savings"] >= Decimal("0.00")


def test_debt_empty_list():
    res = compare_debt_strategies([])
    assert res["avalanche"]["total_months"] == 0
    assert res["snowball"]["total_months"] == 0
