"""Deterministic Financial Calculation Engine for Budgeting and Cashflow."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional


def to_decimal(val: Any) -> Decimal:
    """Safe conversion to Decimal with two decimal places."""
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_budget_status(
    monthly_limit: Decimal,
    total_spent: Decimal,
    alert_threshold_pct: Decimal = Decimal("80.0")
) -> Dict[str, Any]:
    """
    Calculate deterministic budget utilization metrics.
    Handles zero limits, negative spending (refunds), and over-budget states safely.
    """
    limit = to_decimal(monthly_limit)
    spent = to_decimal(total_spent)
    threshold = to_decimal(alert_threshold_pct)

    if limit <= Decimal("0.00"):
        # Zero or negative limit edge case
        pct_used = 100.0 if spent > Decimal("0.00") else 0.0
        remaining = Decimal("0.00")
        is_over = spent > Decimal("0.00")
        is_near = False
    else:
        remaining = limit - spent
        pct_used = float((spent / limit) * Decimal("100.0"))
        is_over = spent > limit
        is_near = (Decimal(str(pct_used)) >= threshold) and not is_over

    return {
        "monthly_limit": limit,
        "spent_amount": spent,
        "remaining_amount": remaining,
        "percentage_used": round(pct_used, 2),
        "is_over_budget": is_over,
        "is_near_limit": is_near
    }


def calculate_cashflow_summary(
    incomes: List[Decimal],
    expenses: List[Decimal]
) -> Dict[str, Any]:
    """
    Calculate deterministic net cash flow and savings rate.
    Savings rate = (Income - Expenses) / Income * 100
    If Income <= 0, savings rate is 0.0%.
    """
    total_inc = sum((to_decimal(i) for i in incomes), Decimal("0.00"))
    total_exp = sum((to_decimal(e) for e in expenses), Decimal("0.00"))
    net_savings = total_inc - total_exp

    if total_inc > Decimal("0.00"):
        savings_rate = float((net_savings / total_inc) * Decimal("100.0"))
    else:
        savings_rate = 0.0

    return {
        "total_income": total_inc,
        "total_expenses": total_exp,
        "net_savings": net_savings,
        "savings_rate_pct": round(savings_rate, 2)
    }


def compare_period_spending(
    current_period_spending: Decimal,
    previous_period_spending: Decimal
) -> Dict[str, Any]:
    """Compare spending across two periods with difference and percentage change."""
    current = to_decimal(current_period_spending)
    prev = to_decimal(previous_period_spending)
    diff = current - prev

    if prev > Decimal("0.00"):
        pct_change = float((diff / prev) * Decimal("100.0"))
    else:
        pct_change = 100.0 if current > Decimal("0.00") else 0.0

    return {
        "current_spending": current,
        "previous_spending": prev,
        "difference": diff,
        "percentage_change": round(pct_change, 2),
        "increased": diff > Decimal("0.00")
    }
