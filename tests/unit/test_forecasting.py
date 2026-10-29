"""Unit tests for Cash-flow forecasting and baseline evaluation."""

from finance_engine.forecasting.cashflow import evaluate_forecast_baseline, forecast_monthly_cashflow


def test_evaluate_forecast_baseline():
    # 6 months of historical expenses with gentle upward trend
    series = [2500.0, 2600.0, 2700.0, 2800.0, 2900.0, 3000.0]
    metrics = evaluate_forecast_baseline(series, test_size=2)
    assert "mae" in metrics
    assert "rmse" in metrics
    assert "baseline_mae" in metrics
    assert metrics["mae"] >= 0.0


def test_forecast_monthly_cashflow():
    incomes = [5000.0, 5000.0, 5200.0, 5200.0]
    expenses = [3000.0, 3100.0, 3050.0, 3200.0]
    res = forecast_monthly_cashflow(incomes, expenses, forecast_months=6)

    assert res["forecast_horizon_months"] == 6
    projs = res["projections"]
    assert len(projs) == 6
    for p in projs:
        # Confidence interval order: lower <= projected <= upper
        assert p["income_lower"] <= p["projected_income"] <= p["income_upper"]
        assert p["expenses_lower"] <= p["projected_expenses"] <= p["expenses_upper"]
        assert p["projected_net_savings"] == round(p["projected_income"] - p["projected_expenses"], 2)
