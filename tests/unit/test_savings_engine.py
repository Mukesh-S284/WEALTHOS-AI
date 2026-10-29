"""Unit tests for savings and emergency fund calculations."""

from datetime import date, timedelta
from decimal import Decimal
from finance_engine.savings.engine import (
    calculate_required_monthly_savings,
    calculate_projected_completion_date,
    calculate_emergency_fund_status
)


def test_required_monthly_savings_linear():
    today = date(2026, 1, 1)
    target_date = date(2026, 11, 1) # ~10 months
    res = calculate_required_monthly_savings(
        target_amount=Decimal("10000.00"),
        current_amount=Decimal("0.00"),
        target_date=target_date,
        current_date=today,
        annual_return_pct=Decimal("0.0")
    )
    assert res["months_remaining"] == 10
    assert res["required_monthly_contribution"] == Decimal("1000.00")
    assert res["is_completed"] is False
    assert res["is_overdue"] is False


def test_required_monthly_savings_with_compound_return():
    today = date(2026, 1, 1)
    target_date = date(2027, 1, 1) # 12 months
    res = calculate_required_monthly_savings(
        target_amount=Decimal("12000.00"),
        current_amount=Decimal("0.00"),
        target_date=target_date,
        current_date=today,
        annual_return_pct=Decimal("6.0")
    )
    assert res["months_remaining"] == 12
    # With 6% return, required monthly is less than simple 1000.00/mo
    assert res["required_monthly_contribution"] < Decimal("1000.00")
    assert res["required_monthly_contribution"] > Decimal("900.00")


def test_required_monthly_savings_edge_cases():
    today = date(2026, 1, 1)
    
    # Already completed
    res_done = calculate_required_monthly_savings(
        target_amount=Decimal("5000.00"),
        current_amount=Decimal("5500.00"),
        target_date=date(2026, 6, 1),
        current_date=today
    )
    assert res_done["is_completed"] is True
    assert res_done["required_monthly_contribution"] == Decimal("0.00")

    # Overdue
    res_overdue = calculate_required_monthly_savings(
        target_amount=Decimal("5000.00"),
        current_amount=Decimal("1000.00"),
        target_date=date(2025, 12, 1),
        current_date=today
    )
    assert res_overdue["is_overdue"] is True
    assert res_overdue["shortfall"] == Decimal("4000.00")


def test_projected_completion_date():
    today = date(2026, 1, 1)
    res = calculate_projected_completion_date(
        target_amount=Decimal("6000.00"),
        current_amount=Decimal("0.00"),
        monthly_contribution=Decimal("500.00"),
        current_date=today
    )
    assert res["months_to_complete"] == 12
    assert res["is_already_completed"] is False


def test_emergency_fund_status():
    # 6 months target = 2000 * 6 = 12,000
    res_full = calculate_emergency_fund_status(
        current_savings=Decimal("15000.00"),
        monthly_essential_expenses=Decimal("2000.00"),
        target_months=6
    )
    assert res_full["months_covered"] == 7.5
    assert res_full["health_status"] == "fully_funded"
    assert res_full["gap_amount"] == Decimal("0.00")

    # Underfunded: 2,000 savings with 2,000 expenses = 1 month
    res_partial = calculate_emergency_fund_status(
        current_savings=Decimal("2000.00"),
        monthly_essential_expenses=Decimal("2000.00"),
        target_months=6
    )
    assert res_partial["months_covered"] == 1.0
    assert res_partial["gap_amount"] == Decimal("10000.00")
    assert res_partial["health_status"] == "partially_funded"
