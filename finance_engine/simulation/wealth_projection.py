"""Deterministic Future-Wealth & Compound Interest Simulation Engine."""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any


def to_decimal(val: Any) -> Decimal:
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_wealth_projection(
    initial_balance: Decimal,
    monthly_contribution: Decimal,
    annual_return_pct: Decimal,
    annual_inflation_pct: Decimal = Decimal("2.5"),
    years: int = 10,
    annual_contribution_step_up_pct: Decimal = Decimal("0.0")
) -> Dict[str, Any]:
    """
    Project compound wealth accumulation year-by-year with inflation purchasing-power adjustment.
    Supports annual contribution step-up (e.g. 5% salary increase applied to SIP).
    """
    p_init = float(to_decimal(initial_balance))
    pmt_init = float(to_decimal(monthly_contribution))
    r_annual = float(to_decimal(annual_return_pct)) / 100.0
    r_monthly = r_annual / 12.0
    inf_annual = float(to_decimal(annual_inflation_pct)) / 100.0
    step_up = float(to_decimal(annual_contribution_step_up_pct)) / 100.0

    current_balance = p_init
    total_contributed = p_init
    current_monthly_pmt = pmt_init
    yearly_milestones = []

    for yr in range(1, years + 1):
        # Accumulate 12 months with monthly compounding
        for _ in range(12):
            # Compound existing balance
            current_balance = (current_balance * (1.0 + r_monthly)) + current_monthly_pmt
            total_contributed += current_monthly_pmt

        # Inflation discount factor
        inflation_deflator = (1.0 + inf_annual) ** yr
        real_balance = current_balance / inflation_deflator if inflation_deflator > 0 else current_balance
        investment_gains = max(0.0, current_balance - total_contributed)

        yearly_milestones.append({
            "year": yr,
            "nominal_balance": round(current_balance, 2),
            "real_inflation_adjusted_balance": round(real_balance, 2),
            "total_contributed_principal": round(total_contributed, 2),
            "total_investment_earnings": round(investment_gains, 2),
            "monthly_contribution_that_year": round(current_monthly_pmt, 2)
        })

        # Apply annual step up for the next year
        current_monthly_pmt *= (1.0 + step_up)

    final_nominal = yearly_milestones[-1]["nominal_balance"] if yearly_milestones else p_init
    final_real = yearly_milestones[-1]["real_inflation_adjusted_balance"] if yearly_milestones else p_init
    final_principal = yearly_milestones[-1]["total_contributed_principal"] if yearly_milestones else p_init
    final_earnings = yearly_milestones[-1]["total_investment_earnings"] if yearly_milestones else 0.0

    return {
        "initial_balance": p_init,
        "initial_monthly_contribution": pmt_init,
        "annual_return_pct": r_annual * 100.0,
        "annual_inflation_pct": inf_annual * 100.0,
        "annual_step_up_pct": step_up * 100.0,
        "years": years,
        "final_nominal_wealth": round(final_nominal, 2),
        "final_real_purchasing_power": round(final_real, 2),
        "total_principal_invested": round(final_principal, 2),
        "total_compound_gains": round(final_earnings, 2),
        "yearly_trajectory": yearly_milestones
    }
