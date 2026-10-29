"""Deterministic Savings & Emergency Fund Calculation Engine."""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
import math


def to_decimal(val: Any) -> Decimal:
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_required_monthly_savings(
    target_amount: Decimal,
    current_amount: Decimal,
    target_date: date,
    current_date: Optional[date] = None,
    annual_return_pct: Decimal = Decimal("0.0")
) -> Dict[str, Any]:
    """
    Calculate required monthly contribution to reach target amount by target date.
    Supports 0% interest (deterministic linear) and compound return.
    Handles overdue goals, zero target, and already completed goals safely.
    """
    target = to_decimal(target_amount)
    current = to_decimal(current_amount)
    annual_return = to_decimal(annual_return_pct)
    today = current_date or date.today()

    if target <= Decimal("0.00"):
        return {
            "required_monthly_contribution": Decimal("0.00"),
            "months_remaining": 0,
            "is_completed": True,
            "is_overdue": False,
            "shortfall": Decimal("0.00")
        }

    shortfall = max(Decimal("0.00"), target - current)
    if shortfall == Decimal("0.00"):
        return {
            "required_monthly_contribution": Decimal("0.00"),
            "months_remaining": 0,
            "is_completed": True,
            "is_overdue": False,
            "shortfall": Decimal("0.00")
        }

    # Month calculation
    days_diff = (target_date - today).days
    if days_diff <= 0:
        return {
            "required_monthly_contribution": shortfall,
            "months_remaining": 0,
            "is_completed": False,
            "is_overdue": True,
            "shortfall": shortfall
        }

    # Fractional months rounded up to at least 1
    months = max(1, math.ceil(days_diff / 30.4375))

    # Without interest (Linear)
    if annual_return <= Decimal("0.00"):
        monthly_req = (shortfall / Decimal(str(months))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        # Sinking Fund PMT formula:
        # FV_needed = target - current * (1 + r)^n
        # PMT = FV_needed * r / ((1 + r)^n - 1)
        monthly_rate = float(annual_return) / 100.0 / 12.0
        n = months
        fv_current = float(current) * ((1.0 + monthly_rate) ** n)
        remaining_fv = float(target) - fv_current
        if remaining_fv <= 0:
            monthly_req = Decimal("0.00")
        else:
            pmt = remaining_fv * monthly_rate / (((1.0 + monthly_rate) ** n) - 1.0)
            monthly_req = Decimal(str(round(pmt, 2)))

    return {
        "required_monthly_contribution": monthly_req,
        "months_remaining": months,
        "is_completed": False,
        "is_overdue": False,
        "shortfall": shortfall
    }


def calculate_projected_completion_date(
    target_amount: Decimal,
    current_amount: Decimal,
    monthly_contribution: Decimal,
    annual_return_pct: Decimal = Decimal("0.0"),
    current_date: Optional[date] = None
) -> Dict[str, Any]:
    """Calculate date when goal will be completed given a monthly contribution rate."""
    target = to_decimal(target_amount)
    current = to_decimal(current_amount)
    monthly = to_decimal(monthly_contribution)
    today = current_date or date.today()

    if current >= target:
        return {
            "projected_date": today,
            "months_to_complete": 0,
            "is_already_completed": True
        }

    if monthly <= Decimal("0.00"):
        return {
            "projected_date": None,
            "months_to_complete": None,
            "is_already_completed": False,
            "message": "Monthly contribution is zero; goal cannot be reached."
        }

    shortfall = target - current
    if annual_return_pct <= Decimal("0.00"):
        months = math.ceil(float(shortfall) / float(monthly))
    else:
        monthly_rate = float(annual_return_pct) / 100.0 / 12.0
        # Formula: n = ln((FV * r / PMT) + 1) / ln(1 + r)
        try:
            val = (float(shortfall) * monthly_rate / float(monthly)) + 1.0
            months = math.ceil(math.log(val) / math.log(1.0 + monthly_rate))
        except (ValueError, ZeroDivisionError):
            months = math.ceil(float(shortfall) / float(monthly))

    projected_date = today + timedelta(days=int(months * 30.4375))
    return {
        "projected_date": projected_date,
        "months_to_complete": months,
        "is_already_completed": False
    }


def calculate_emergency_fund_status(
    current_savings: Decimal,
    monthly_essential_expenses: Decimal,
    target_months: int = 6
) -> Dict[str, Any]:
    """
    Evaluate emergency fund adequacy.
    Target emergency fund = monthly_essential_expenses * target_months.
    Calculates coverage ratio (months covered) and gap.
    """
    savings = to_decimal(current_savings)
    expenses = to_decimal(monthly_essential_expenses)

    if expenses <= Decimal("0.00"):
        return {
            "target_months": target_months,
            "target_amount": Decimal("0.00"),
            "current_savings": savings,
            "months_covered": 99.0 if savings > 0 else 0.0,
            "gap_amount": Decimal("0.00"),
            "health_status": "fully_funded" if savings > 0 else "unspecified"
        }

    target_amount = expenses * Decimal(str(target_months))
    months_covered = float(savings / expenses)
    gap = max(Decimal("0.00"), target_amount - savings)

    if months_covered >= target_months:
        status = "fully_funded"
    elif months_covered >= 3.0:
        status = "moderately_funded"
    elif months_covered >= 1.0:
        status = "partially_funded"
    else:
        status = "critically_underfunded"

    return {
        "target_months": target_months,
        "monthly_essential_expenses": expenses,
        "target_amount": target_amount,
        "current_savings": savings,
        "months_covered": round(months_covered, 1),
        "gap_amount": gap,
        "health_status": status
    }
