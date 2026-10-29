"""Cash-Flow Forecasting Engine: Trend & Baseline Models with Chronological Evaluation."""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Tuple
import numpy as np


def to_decimal(val: Any) -> Decimal:
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def evaluate_forecast_baseline(
    series: List[float],
    test_size: int = 3
) -> Dict[str, float]:
    """
    Chronological validation comparing Moving Average baseline against Linear Trend.
    Prevents data leakage by strictly training on earlier months and evaluating on later months.
    """
    if len(series) <= test_size + 2:
        return {"mae": 0.0, "rmse": 0.0, "baseline_mae": 0.0}

    train = series[:-test_size]
    test = series[-test_size:]

    # Baseline 1: Last 3-month rolling mean
    rolling_mean = float(np.mean(train[-3:])) if len(train) >= 3 else float(np.mean(train))
    baseline_errors = [abs(actual - rolling_mean) for actual in test]
    baseline_mae = float(np.mean(baseline_errors))

    # Model: Linear Trend (OLS on time index)
    x_train = np.arange(len(train))
    poly = np.polyfit(x_train, train, deg=1)
    x_test = np.arange(len(train), len(train) + len(test))
    trend_preds = np.polyval(poly, x_test)

    trend_errors = [abs(actual - pred) for actual, pred in zip(test, trend_preds)]
    mae = float(np.mean(trend_errors))
    rmse = float(np.sqrt(np.mean([(actual - pred)**2 for actual, pred in zip(test, trend_preds)])))

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "baseline_mae": round(baseline_mae, 2),
        "model_superior": mae <= baseline_mae
    }


def forecast_monthly_cashflow(
    monthly_incomes: List[float],
    monthly_expenses: List[float],
    forecast_months: int = 6
) -> Dict[str, Any]:
    """
    Project future monthly incomes, expenses, and net surplus with confidence bounds.
    If historical observations are scarce (<3 months), uses conservative moving statistics.
    """
    n_forecast = max(1, min(forecast_months, 36))

    # Helper for single series forecast
    def _project_series(data: List[float], default_val: float) -> Tuple[List[float], List[float], List[float]]:
        if not data:
            data = [default_val]
        
        arr = np.array(data, dtype=float)
        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr, ddof=1)) if len(arr) > 1 else (mean_val * 0.10)
        
        # If sufficient history, fit gentle trend
        if len(arr) >= 4:
            x = np.arange(len(arr))
            poly = np.polyfit(x, arr, deg=1)
            # Dampen slope to avoid unrealistic divergence
            slope = poly[0] * 0.5
            intercept = poly[1]
            future_x = np.arange(len(arr), len(arr) + n_forecast)
            point_forecast = [float(max(0.0, intercept + slope * fx)) for fx in future_x]
        else:
            point_forecast = [mean_val] * n_forecast

        # 80% confidence interval: z ~ 1.28
        lower_bounds = [max(0.0, pt - 1.28 * std_val) for pt in point_forecast]
        upper_bounds = [pt + 1.28 * std_val for pt in point_forecast]
        return point_forecast, lower_bounds, upper_bounds

    inc_pts, inc_low, inc_high = _project_series(monthly_incomes, default_val=5000.0)
    exp_pts, exp_low, exp_high = _project_series(monthly_expenses, default_val=3500.0)

    # Historical model performance evaluation if enough observations
    eval_metrics = evaluate_forecast_baseline(monthly_expenses, test_size=2) if len(monthly_expenses) >= 5 else None

    projections = []
    for m in range(n_forecast):
        net = inc_pts[m] - exp_pts[m]
        projections.append({
            "month_offset": m + 1,
            "projected_income": round(inc_pts[m], 2),
            "income_lower": round(inc_low[m], 2),
            "income_upper": round(inc_high[m], 2),
            "projected_expenses": round(exp_pts[m], 2),
            "expenses_lower": round(exp_low[m], 2),
            "expenses_upper": round(exp_high[m], 2),
            "projected_net_savings": round(net, 2)
        })

    return {
        "forecast_horizon_months": n_forecast,
        "historical_data_points": len(monthly_expenses),
        "validation_metrics": eval_metrics,
        "projections": projections
    }
