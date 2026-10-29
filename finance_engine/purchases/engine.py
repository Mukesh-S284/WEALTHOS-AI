"""Smart Purchase Decision Engine: Affordability, Buffer Analysis & Scenario Comparisons."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
import math


def to_decimal(val: Any) -> Decimal:
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_loan_payment(principal: Decimal, annual_interest_rate_pct: Decimal, tenure_months: int) -> Dict[str, Any]:
    """Calculate monthly installment and total financing cost."""
    p = float(to_decimal(principal))
    apr = float(to_decimal(annual_interest_rate_pct))
    n = max(1, tenure_months)

    if apr <= 0.0:
        monthly_pmt = round(p / n, 2)
        total_interest = 0.0
    else:
        r = apr / 100.0 / 12.0
        # PMT = P * [r(1+r)^n] / [(1+r)^n - 1]
        monthly_pmt = round(p * (r * ((1.0 + r) ** n)) / (((1.0 + r) ** n) - 1.0), 2)
        total_interest = round((monthly_pmt * n) - p, 2)

    total_cost = round(p + total_interest, 2)

    return {
        "monthly_payment": Decimal(str(monthly_pmt)),
        "total_interest": Decimal(str(max(0.0, total_interest))),
        "total_cost": Decimal(str(total_cost)),
        "tenure_months": n
    }


def evaluate_purchase_decision(
    purchase_price: Decimal,
    available_liquid_savings: Decimal,
    monthly_net_surplus: Decimal,
    minimum_cash_buffer: Decimal,
    financing_apr: Decimal = Decimal("9.99"),
    financing_tenure_months: int = 12,
    alternative_price: Optional[Decimal] = None
) -> Dict[str, Any]:
    """
    Evaluate 5 purchase scenarios deterministically with transparent trade-offs.
    Scenarios:
    1. Buy Now with Cash
    2. Wait & Save
    3. Lower-Cost Alternative
    4. Financing / Installment
    5. Comparison & Recommendation Matrix
    """
    price = to_decimal(purchase_price)
    savings = to_decimal(available_liquid_savings)
    surplus = to_decimal(monthly_net_surplus)
    buffer = to_decimal(minimum_cash_buffer)

    # 1. Buy Now Cash
    cash_remaining = savings - price
    violates_buffer = cash_remaining < buffer
    can_afford_cash = savings >= price

    if surplus > Decimal("0.00") and violates_buffer:
        buffer_deficit = buffer - max(Decimal("0.00"), cash_remaining)
        rebuild_months = math.ceil(float(buffer_deficit) / float(surplus))
    elif violates_buffer:
        rebuild_months = 999 # Cannot rebuild without surplus
    else:
        rebuild_months = 0

    buy_now_scenario = {
        "scenario": "buy_now_cash",
        "feasible": bool(can_afford_cash),
        "cash_remaining": cash_remaining,
        "violates_buffer": bool(violates_buffer),
        "buffer_deficit": max(Decimal("0.00"), buffer - cash_remaining),
        "months_to_rebuild_buffer": rebuild_months,
        "total_cost": price
    }

    # 2. Wait and Save
    if surplus > Decimal("0.00"):
        wait_months = math.ceil(float(price) / float(surplus))
    else:
        wait_months = None

    wait_and_save_scenario = {
        "scenario": "wait_and_save",
        "feasible": bool(surplus > Decimal("0.00")),
        "months_to_save": wait_months,
        "cash_buffer_intact": True,
        "total_cost": price
    }

    # 3. Lower Cost Alternative
    alt_scenario = None
    if alternative_price and to_decimal(alternative_price) < price:
        alt_p = to_decimal(alternative_price)
        alt_remaining = savings - alt_p
        alt_violates = alt_remaining < buffer
        alt_savings_amount = price - alt_p
        alt_scenario = {
            "scenario": "lower_cost_alternative",
            "alternative_price": alt_p,
            "cost_savings": alt_savings_amount,
            "cash_remaining": alt_remaining,
            "violates_buffer": bool(alt_violates)
        }

    # 4. Financing
    loan_metrics = calculate_loan_payment(price, financing_apr, financing_tenure_months)
    monthly_installment = loan_metrics["monthly_payment"]
    remaining_monthly_surplus = surplus - monthly_installment
    financing_feasible = remaining_monthly_surplus >= Decimal("0.00")

    financing_scenario = {
        "scenario": "financing",
        "feasible": bool(financing_feasible),
        "monthly_payment": monthly_installment,
        "tenure_months": financing_tenure_months,
        "apr_pct": financing_apr,
        "total_interest_paid": loan_metrics["total_interest"],
        "total_cost": loan_metrics["total_cost"],
        "post_purchase_monthly_surplus": remaining_monthly_surplus,
        "cash_buffer_retained": savings
    }

    # 5. Synthesis & Risk Level
    if not can_afford_cash and not financing_feasible:
        verdict = "NOT_RECOMMENDED_UNAFFORDABLE"
        verdict_summary = "Purchase exceeds available savings and loan repayments exceed monthly surplus."
    elif can_afford_cash and not violates_buffer:
        verdict = "AFFORDABLE_CASH"
        verdict_summary = "You can comfortably purchase with cash while keeping your emergency cash buffer intact."
    elif can_afford_cash and violates_buffer:
        verdict = "CAUTION_BUFFER_DEPLETION"
        verdict_summary = f"You have enough cash, but this will reduce your emergency buffer below your minimum threshold by {buy_now_scenario['buffer_deficit']}. Rebuilding will take {rebuild_months} months."
    elif financing_feasible:
        verdict = "FINANCING_POSSIBLE_WITH_INTEREST"
        verdict_summary = f"Financing is technically affordable from cashflow, but adds {loan_metrics['total_interest']} in interest costs."
    else:
        verdict = "WAIT_AND_SAVE_RECOMMENDED"
        verdict_summary = f"Waiting and saving for {wait_months} months is the safest path to preserve your buffer."

    return {
        "purchase_price": price,
        "available_liquid_savings": savings,
        "monthly_net_surplus": surplus,
        "minimum_cash_buffer": buffer,
        "verdict": verdict,
        "verdict_summary": verdict_summary,
        "scenarios": {
            "buy_now_cash": buy_now_scenario,
            "wait_and_save": wait_and_save_scenario,
            "lower_cost_alternative": alt_scenario,
            "financing": financing_scenario
        }
    }
