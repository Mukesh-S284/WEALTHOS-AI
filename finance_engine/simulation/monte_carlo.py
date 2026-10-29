"""Monte Carlo Stochastic Wealth Simulation Engine."""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
import numpy as np


def to_decimal(val: Any) -> Decimal:
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def run_monte_carlo_simulation(
    initial_wealth: Decimal,
    monthly_contribution: Decimal,
    expected_annual_return_pct: Decimal,
    annual_volatility_pct: Decimal,
    years: int = 15,
    num_simulations: int = 1000,
    target_wealth: Optional[Decimal] = None,
    annual_inflation_pct: Decimal = Decimal("2.5"),
    random_seed: Optional[int] = 42
) -> Dict[str, Any]:
    """
    Run stochastic Monte Carlo simulation using Geometric Brownian Motion with periodic cash additions.
    Returns percentile distributions (P10, P25, P50, P75, P90) over time and goal achievement probability.
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    w0 = float(to_decimal(initial_wealth))
    c_monthly = float(to_decimal(monthly_contribution))
    mu_annual = float(to_decimal(expected_annual_return_pct)) / 100.0
    sigma_annual = float(to_decimal(annual_volatility_pct)) / 100.0
    inf_annual = float(to_decimal(annual_inflation_pct)) / 100.0
    n_sims = max(100, min(num_simulations, 5000))
    n_years = max(1, min(years, 40))
    n_months = n_years * 12

    # Monthly parameters for Geometric Brownian Motion
    dt = 1.0 / 12.0
    drift_monthly = (mu_annual - 0.5 * (sigma_annual ** 2)) * dt
    vol_monthly = sigma_annual * np.sqrt(dt)

    # Pre-generate standard normal random matrix: [n_sims, n_months]
    random_shocks = np.random.normal(0.0, 1.0, size=(n_sims, n_months))

    # Wealth trajectory matrix: [n_sims, n_years + 1] to store yearly milestones
    yearly_paths = np.zeros((n_sims, n_years + 1))
    yearly_paths[:, 0] = w0

    current_wealth = np.full(n_sims, w0)

    for m in range(n_months):
        # Monthly return shock: exp(drift + vol * z)
        monthly_return_factors = np.exp(drift_monthly + vol_monthly * random_shocks[:, m])
        # Add monthly contribution then apply return factor
        current_wealth = (current_wealth + c_monthly) * monthly_return_factors
        # Ensure wealth cannot fall below 0
        current_wealth = np.maximum(0.0, current_wealth)

        # Record at end of each year
        if (m + 1) % 12 == 0:
            yr_idx = (m + 1) // 12
            yearly_paths[:, yr_idx] = current_wealth

    # Calculate percentiles across all paths for each year
    milestones = []
    for yr in range(n_years + 1):
        col = yearly_paths[:, yr]
        p10 = float(np.percentile(col, 10))
        p25 = float(np.percentile(col, 25))
        p50 = float(np.percentile(col, 50))
        p75 = float(np.percentile(col, 75))
        p90 = float(np.percentile(col, 90))

        # Inflation adjusted median
        deflator = (1.0 + inf_annual) ** yr if yr > 0 else 1.0
        p50_real = p50 / deflator

        milestones.append({
            "year": yr,
            "p10_bearish": round(p10, 2),
            "p25_conservative": round(p25, 2),
            "p50_median": round(p50, 2),
            "p75_optimistic": round(p75, 2),
            "p90_bullish": round(p90, 2),
            "median_real_purchasing_power": round(p50_real, 2)
        })

    # Final wealth distribution metrics
    final_wealths = yearly_paths[:, -1]
    final_median = float(np.median(final_wealths))
    final_mean = float(np.mean(final_wealths))

    # Probability of meeting target
    success_prob = None
    target_val = None
    if target_wealth is not None and target_wealth > 0:
        target_val = float(to_decimal(target_wealth))
        successful_paths = np.sum(final_wealths >= target_val)
        success_prob = round(float(successful_paths / n_sims) * 100.0, 1)

    return {
        "model_type": "Geometric Brownian Motion (Log-Normal Distribution)",
        "assumptions": {
            "initial_wealth": w0,
            "monthly_contribution": c_monthly,
            "expected_annual_return_pct": mu_annual * 100.0,
            "annual_volatility_pct": sigma_annual * 100.0,
            "annual_inflation_pct": inf_annual * 100.0,
            "simulation_runs": n_sims,
            "years": n_years,
            "random_seed": random_seed
        },
        "target_wealth": target_val,
        "probability_of_reaching_target_pct": success_prob,
        "final_outcomes": {
            "p10_bearish": milestones[-1]["p10_bearish"],
            "p25_conservative": milestones[-1]["p25_conservative"],
            "p50_median": milestones[-1]["p50_median"],
            "p75_optimistic": milestones[-1]["p75_optimistic"],
            "p90_bullish": milestones[-1]["p90_bullish"],
            "mean_wealth": round(final_mean, 2)
        },
        "yearly_percentiles": milestones,
        "disclaimer": "Monte Carlo simulations illustrate hypothetical distribution of returns under assumed volatility and drift parameters. They do not guarantee market performance or account for black-swan non-normal market events."
    }
