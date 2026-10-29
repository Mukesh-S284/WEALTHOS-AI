"""Unit tests for deterministic budget engine calculations."""

from decimal import Decimal
from finance_engine.budgeting.engine import (
    calculate_budget_status,
    calculate_cashflow_summary,
    compare_period_spending
)


def test_budget_status_under_limit():
    res = calculate_budget_status(
        monthly_limit=Decimal("500.00"),
        total_spent=Decimal("250.00"),
        alert_threshold_pct=Decimal("80.0")
    )
    assert res["monthly_limit"] == Decimal("500.00")
    assert res["spent_amount"] == Decimal("250.00")
    assert res["remaining_amount"] == Decimal("250.00")
    assert res["percentage_used"] == 50.0
    assert res["is_over_budget"] is False
    assert res["is_near_limit"] is False


def test_budget_status_near_limit_alert():
    res = calculate_budget_status(
        monthly_limit=Decimal("1000.00"),
        total_spent=Decimal("850.00"),
        alert_threshold_pct=Decimal("80.0")
    )
    assert res["remaining_amount"] == Decimal("150.00")
    assert res["percentage_used"] == 85.0
    assert res["is_over_budget"] is False
    assert res["is_near_limit"] is True


def test_budget_status_over_budget():
    res = calculate_budget_status(
        monthly_limit=Decimal("400.00"),
        total_spent=Decimal("450.00"),
        alert_threshold_pct=Decimal("80.0")
    )
    assert res["remaining_amount"] == Decimal("-50.00")
    assert res["percentage_used"] == 112.5
    assert res["is_over_budget"] is True
    assert res["is_near_limit"] is False


def test_budget_status_zero_limit_edge_case():
    res = calculate_budget_status(
        monthly_limit=Decimal("0.00"),
        total_spent=Decimal("50.00")
    )
    assert res["is_over_budget"] is True
    assert res["percentage_used"] == 100.0


def test_cashflow_summary_standard():
    incomes = [Decimal("3000.00"), Decimal("1500.00")]
    expenses = [Decimal("1200.00"), Decimal("800.00"), Decimal("500.00")]
    summary = calculate_cashflow_summary(incomes, expenses)
    
    assert summary["total_income"] == Decimal("4500.00")
    assert summary["total_expenses"] == Decimal("2500.00")
    assert summary["net_savings"] == Decimal("2000.00")
    # (2000 / 4500) * 100 = 44.44%
    assert summary["savings_rate_pct"] == 44.44


def test_cashflow_summary_zero_income():
    incomes = []
    expenses = [Decimal("500.00")]
    summary = calculate_cashflow_summary(incomes, expenses)
    assert summary["total_income"] == Decimal("0.00")
    assert summary["net_savings"] == Decimal("-500.00")
    assert summary["savings_rate_pct"] == 0.0


def test_compare_period_spending():
    res = compare_period_spending(
        current_period_spending=Decimal("1200.00"),
        previous_period_spending=Decimal("1000.00")
    )
    assert res["difference"] == Decimal("200.00")
    assert res["percentage_change"] == 20.0
    assert res["increased"] is True
