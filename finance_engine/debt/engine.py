"""Debt Repayment Engine: Avalanche vs Snowball strategies and amortization."""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any
from copy import deepcopy


def to_decimal(val: Any) -> Decimal:
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def simulate_debt_payoff(
    debts: List[Dict[str, Any]],
    extra_monthly_payment: Decimal = Decimal("0.00"),
    strategy: str = "avalanche"
) -> Dict[str, Any]:
    """
    Simulate debt repayment under 'avalanche' (highest APR first) or 'snowball' (lowest balance first).
    Each debt item must contain: name, balance, apr, min_payment.
    """
    if not debts:
        return {
            "strategy": strategy,
            "total_months": 0,
            "total_interest_paid": Decimal("0.00"),
            "total_principal_paid": Decimal("0.00"),
            "debts_payoff_order": []
        }

    # Deep copy debts for simulation
    active_debts = []
    total_principal = Decimal("0.00")
    for d in debts:
        bal = to_decimal(d.get("balance", 0))
        if bal > Decimal("0.00"):
            total_principal += bal
            active_debts.append({
                "name": str(d.get("name", "Debt")),
                "balance": bal,
                "apr": float(to_decimal(d.get("apr", 0))),
                "min_payment": to_decimal(d.get("min_payment", 0)),
                "months_to_pay": 0
            })

    if not active_debts:
        return {
            "strategy": strategy,
            "total_months": 0,
            "total_interest_paid": Decimal("0.00"),
            "total_principal_paid": Decimal("0.00"),
            "debts_payoff_order": []
        }

    extra = to_decimal(extra_monthly_payment)
    total_interest_paid = Decimal("0.00")
    month = 0
    payoff_order = []
    max_months = 360  # 30 years safety cap

    while active_debts and month < max_months:
        month += 1
        
        # 1. Apply monthly interest to each active debt
        for d in active_debts:
            monthly_rate = d["apr"] / 100.0 / 12.0
            interest = (d["balance"] * Decimal(str(monthly_rate))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            d["balance"] += interest
            total_interest_paid += interest

        # 2. Pay minimums
        freed_cashflow = Decimal("0.00")
        for d in active_debts:
            payment = min(d["balance"], d["min_payment"])
            d["balance"] -= payment
            # If min payment was more than balance, excess becomes freed
            if d["balance"] == Decimal("0.00"):
                freed_cashflow += (d["min_payment"] - payment)

        # 3. Sort target debt according to strategy
        if strategy.lower() == "avalanche":
            active_debts.sort(key=lambda x: x["apr"], reverse=True)
        else: # snowball
            active_debts.sort(key=lambda x: x["balance"])

        # 4. Apply extra payment + freed cashflow to top priority debt
        available_extra = extra + freed_cashflow
        for d in active_debts:
            if available_extra <= Decimal("0.00"):
                break
            pay_amt = min(d["balance"], available_extra)
            d["balance"] -= pay_amt
            available_extra -= pay_amt

        # 5. Check completed debts
        remaining = []
        for d in active_debts:
            if d["balance"] <= Decimal("0.00"):
                d["months_to_pay"] = month
                payoff_order.append({
                    "name": d["name"],
                    "month_paid_off": month
                })
            else:
                remaining.append(d)
        active_debts = remaining

    return {
        "strategy": strategy,
        "total_months": month,
        "total_interest_paid": total_interest_paid,
        "total_principal_paid": total_principal,
        "total_paid": total_principal + total_interest_paid,
        "debts_payoff_order": payoff_order
    }


def compare_debt_strategies(
    debts: List[Dict[str, Any]],
    extra_monthly_payment: Decimal = Decimal("0.00")
) -> Dict[str, Any]:
    """Run and compare both Avalanche and Snowball payoff strategies side by side."""
    avalanche = simulate_debt_payoff(debts, extra_monthly_payment, strategy="avalanche")
    snowball = simulate_debt_payoff(debts, extra_monthly_payment, strategy="snowball")

    interest_diff = snowball["total_interest_paid"] - avalanche["total_interest_paid"]
    months_diff = snowball["total_months"] - avalanche["total_months"]

    return {
        "avalanche": avalanche,
        "snowball": snowball,
        "avalanche_interest_savings": max(Decimal("0.00"), interest_diff),
        "avalanche_months_saved": max(0, months_diff),
        "recommendation": (
            "Avalanche minimizes total interest paid and gets you debt-free fastest."
            if interest_diff > 0 else
            "Both strategies yield identical timelines. Snowball is recommended for quick early wins."
        )
    }
