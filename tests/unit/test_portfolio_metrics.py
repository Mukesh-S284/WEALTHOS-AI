"""Unit tests for Portfolio analytics, risk metrics, and stress tests."""

from decimal import Decimal
from finance_engine.portfolio.metrics import (
    calculate_portfolio_weights_and_allocation,
    calculate_historical_risk_metrics,
    simulate_portfolio_stress_scenarios
)


def test_portfolio_weights_and_allocation():
    holdings = [
        {
            "symbol": "SPY", "asset_class": "equity", "quantity": 10,
            "average_buy_price": Decimal("400.00"), "current_price": Decimal("500.00")
        },
        {
            "symbol": "BND", "asset_class": "bond", "quantity": 50,
            "average_buy_price": Decimal("75.00"), "current_price": Decimal("72.00")
        },
        {
            "symbol": "GLD", "asset_class": "gold", "quantity": 5,
            "average_buy_price": Decimal("180.00"), "current_price": Decimal("200.00")
        }
    ]

    res = calculate_portfolio_weights_and_allocation(holdings)
    # Total Value: (10*500) + (50*72) + (5*200) = 5000 + 3600 + 1000 = 9600.00
    assert res["total_value"] == Decimal("9600.00")
    # Total Cost: (10*400) + (50*75) + (5*180) = 4000 + 3750 + 900 = 8650.00
    assert res["total_cost"] == Decimal("8650.00")
    assert res["total_gain_loss"] == Decimal("950.00")

    # Asset class percentages
    alloc = res["asset_class_allocation_pct"]
    assert "equity" in alloc
    assert "bond" in alloc
    assert "gold" in alloc
    # 5000 / 9600 = 52.08%
    assert 51.0 <= alloc["equity"] <= 53.0
    # Concentration HHI is between 0 and 1
    assert 0.0 < res["concentration_hhi"] <= 1.0


def test_historical_risk_metrics():
    # Simulating a series with an upward trend and a drawdown
    prices = [100.0, 105.0, 110.0, 95.0, 90.0, 105.0, 115.0, 120.0]
    metrics = calculate_historical_risk_metrics(prices, annual_risk_free_rate=0.04)

    assert metrics["observation_count"] == 8
    assert metrics["annualized_volatility_pct"] > 0.0
    # Max drawdown happened from peak 110.0 down to 90.0 = (90 - 110) / 110 = -18.18%
    assert metrics["max_drawdown_pct"] < 0.0
    assert -25.0 <= metrics["max_drawdown_pct"] <= -15.0


def test_simulate_portfolio_stress_scenarios():
    alloc = {"equity": 60.0, "bond": 30.0, "gold": 10.0}
    total_val = Decimal("100000.00")
    results = simulate_portfolio_stress_scenarios(alloc, total_val)

    assert len(results) == 3
    # 2008 GFC scenario: equity -37%, bond +20%, gold +5%
    # Expected impact: (0.60 * -0.37) + (0.30 * 0.20) + (0.10 * 0.05) = -0.222 + 0.06 + 0.005 = -0.157 (-15.7%)
    gfc = next(r for r in results if "2008" in r["scenario_name"])
    assert -17.0 <= gfc["estimated_impact_pct"] <= -14.0
    assert gfc["estimated_dollar_impact"] < Decimal("0.00")
    assert gfc["projected_portfolio_value"] < total_val
