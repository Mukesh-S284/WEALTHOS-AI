"""Unit tests for Wealth Projections and Monte Carlo Simulation."""

from decimal import Decimal
from finance_engine.simulation.wealth_projection import calculate_wealth_projection
from finance_engine.simulation.monte_carlo import run_monte_carlo_simulation


def test_wealth_projection_zero_return():
    # 10,000 start + 1,000/month for 5 years at 0% return = 10,000 + 60,000 = 70,000
    res = calculate_wealth_projection(
        initial_balance=Decimal("10000.00"),
        monthly_contribution=Decimal("1000.00"),
        annual_return_pct=Decimal("0.0"),
        annual_inflation_pct=Decimal("0.0"),
        years=5
    )
    assert res["final_nominal_wealth"] == 70000.0
    assert res["total_principal_invested"] == 70000.0
    assert res["total_compound_gains"] == 0.0


def test_wealth_projection_compound_growth():
    res = calculate_wealth_projection(
        initial_balance=Decimal("10000.00"),
        monthly_contribution=Decimal("500.00"),
        annual_return_pct=Decimal("8.0"),
        annual_inflation_pct=Decimal("2.5"),
        years=10
    )
    # Compound nominal wealth must exceed total principal invested
    assert res["final_nominal_wealth"] > res["total_principal_invested"]
    # Inflation adjusted real purchasing power must be less than nominal wealth
    assert res["final_real_purchasing_power"] < res["final_nominal_wealth"]
    assert len(res["yearly_trajectory"]) == 10


def test_monte_carlo_percentiles_order_and_seed_reproducibility():
    args = dict(
        initial_wealth=Decimal("50000.00"),
        monthly_contribution=Decimal("1000.00"),
        expected_annual_return_pct=Decimal("9.0"),
        annual_volatility_pct=Decimal("16.0"),
        years=10,
        num_simulations=500,
        target_wealth=Decimal("250000.00"),
        random_seed=42
    )

    res1 = run_monte_carlo_simulation(**args)
    res2 = run_monte_carlo_simulation(**args)

    # Identical with same seed
    assert res1["final_outcomes"]["p50_median"] == res2["final_outcomes"]["p50_median"]
    assert res1["probability_of_reaching_target_pct"] == res2["probability_of_reaching_target_pct"]

    # Verify monotonic percentile order
    p10 = res1["final_outcomes"]["p10_bearish"]
    p25 = res1["final_outcomes"]["p25_conservative"]
    p50 = res1["final_outcomes"]["p50_median"]
    p75 = res1["final_outcomes"]["p75_optimistic"]
    p90 = res1["final_outcomes"]["p90_bullish"]

    assert p10 <= p25 <= p50 <= p75 <= p90
    assert 0.0 <= res1["probability_of_reaching_target_pct"] <= 100.0
