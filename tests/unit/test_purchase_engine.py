"""Unit tests for Smart Purchase Decision Engine."""

from decimal import Decimal
from finance_engine.purchases.engine import calculate_loan_payment, evaluate_purchase_decision


def test_calculate_loan_payment():
    # 0% interest
    res_zero = calculate_loan_payment(Decimal("1200.00"), Decimal("0.0"), 12)
    assert res_zero["monthly_payment"] == Decimal("100.00")
    assert res_zero["total_interest"] == Decimal("0.00")

    # 10% APR over 12 months for 10,000
    res_interest = calculate_loan_payment(Decimal("10000.00"), Decimal("10.0"), 12)
    assert res_interest["monthly_payment"] > Decimal("870.00")
    assert res_interest["total_interest"] > Decimal("500.00")


def test_evaluate_purchase_affordable_cash():
    # Price: 2,000, Savings: 10,000, Buffer: 3,000, Surplus: 800
    res = evaluate_purchase_decision(
        purchase_price=Decimal("2000.00"),
        available_liquid_savings=Decimal("10000.00"),
        monthly_net_surplus=Decimal("800.00"),
        minimum_cash_buffer=Decimal("3000.00")
    )
    assert res["verdict"] == "AFFORDABLE_CASH"
    buy_now = res["scenarios"]["buy_now_cash"]
    assert buy_now["cash_remaining"] == Decimal("8000.00")
    assert buy_now["violates_buffer"] is False
    assert buy_now["months_to_rebuild_buffer"] == 0


def test_evaluate_purchase_dips_into_buffer():
    # Price: 6,000, Savings: 8,000, Buffer: 5,000, Surplus: 1,000
    # Remaining: 2,000 (< 5,000 buffer) -> Deficit 3,000 -> 3 months rebuild
    res = evaluate_purchase_decision(
        purchase_price=Decimal("6000.00"),
        available_liquid_savings=Decimal("8000.00"),
        monthly_net_surplus=Decimal("1000.00"),
        minimum_cash_buffer=Decimal("5000.00")
    )
    assert res["verdict"] == "CAUTION_BUFFER_DEPLETION"
    buy_now = res["scenarios"]["buy_now_cash"]
    assert buy_now["violates_buffer"] is True
    assert buy_now["buffer_deficit"] == Decimal("3000.00")
    assert buy_now["months_to_rebuild_buffer"] == 3


def test_evaluate_purchase_unaffordable():
    # Price: 25,000, Savings: 2,000, Surplus: 100, Buffer: 5,000
    res = evaluate_purchase_decision(
        purchase_price=Decimal("25000.00"),
        available_liquid_savings=Decimal("2000.00"),
        monthly_net_surplus=Decimal("100.00"),
        minimum_cash_buffer=Decimal("5000.00")
    )
    assert res["verdict"] == "NOT_RECOMMENDED_UNAFFORDABLE"
    assert res["scenarios"]["buy_now_cash"]["feasible"] is False
