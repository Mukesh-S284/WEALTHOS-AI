"""Deterministic Portfolio Analytics & Risk Calculation Engine."""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
import math
import numpy as np


def to_decimal(val: Any) -> Decimal:
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_portfolio_weights_and_allocation(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate market value, unrealized gain/loss, asset class weights, and concentration.
    Each holding dict must contain: symbol, asset_class, quantity, average_buy_price, current_price.
    """
    total_cost = Decimal("0.00")
    total_value = Decimal("0.00")
    holding_details = []
    asset_class_totals: Dict[str, Decimal] = {}

    for h in holdings:
        qty = Decimal(str(h.get("quantity", 0)))
        buy_p = Decimal(str(h.get("average_buy_price", 0)))
        cur_p = Decimal(str(h.get("current_price") or buy_p))
        asset_class = str(h.get("asset_class", "equity")).lower()

        cost = (qty * buy_p).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        val = (qty * cur_p).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        gain_loss = val - cost
        gain_loss_pct = float((gain_loss / cost) * Decimal("100.0")) if cost > 0 else 0.0

        total_cost += cost
        total_value += val
        asset_class_totals[asset_class] = asset_class_totals.get(asset_class, Decimal("0.00")) + val

        holding_details.append({
            "symbol": str(h.get("symbol", "")).upper(),
            "name": h.get("name"),
            "asset_class": asset_class,
            "quantity": float(qty),
            "average_buy_price": buy_p,
            "current_price": cur_p,
            "total_cost": cost,
            "current_value": val,
            "unrealized_gain_loss": gain_loss,
            "gain_loss_pct": round(gain_loss_pct, 2)
        })

    # Allocation weights and concentration
    total_gain_loss = total_value - total_cost
    total_gain_loss_pct = float((total_gain_loss / total_cost) * Decimal("100.0")) if total_cost > 0 else 0.0

    asset_class_alloc: Dict[str, float] = {}
    weights: List[float] = []

    for h in holding_details:
        w = float(h["current_value"] / total_value) if total_value > 0 else 0.0
        h["weight_pct"] = round(w * 100.0, 2)
        weights.append(w)

    for ac, ac_val in asset_class_totals.items():
        ac_pct = float((ac_val / total_value) * Decimal("100.0")) if total_value > 0 else 0.0
        asset_class_alloc[ac] = round(ac_pct, 2)

    # Herfindahl-Hirschman Index (HHI) for concentration
    hhi = sum((w ** 2 for w in weights)) if weights else 0.0
    sorted_weights = sorted(weights, reverse=True)
    top3_concentration = sum(sorted_weights[:3]) * 100.0 if sorted_weights else 0.0

    return {
        "total_cost": total_cost,
        "total_value": total_value,
        "total_gain_loss": total_gain_loss,
        "total_gain_loss_pct": round(total_gain_loss_pct, 2),
        "holdings": holding_details,
        "asset_class_allocation_pct": asset_class_alloc,
        "concentration_hhi": round(hhi, 4),
        "top3_concentration_pct": round(top3_concentration, 2)
    }


def calculate_historical_risk_metrics(
    daily_prices: List[float],
    annual_risk_free_rate: float = 0.04
) -> Dict[str, Any]:
    """
    Calculate annualized volatility, maximum drawdown, and Sharpe ratio from a price series.
    Formula conventions:
    - Annualized volatility: std(daily_returns) * sqrt(252)
    - Max drawdown: min((Price - Running_Max) / Running_Max)
    - Sharpe: (Annualized_Return - Rf) / Annualized_Volatility
    """
    if len(daily_prices) < 2:
        return {
            "annualized_return_pct": 0.0,
            "annualized_volatility_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe_ratio": 0.0,
            "observation_count": len(daily_prices)
        }

    prices = np.array(daily_prices, dtype=float)
    returns = np.diff(prices) / prices[:-1]
    
    if len(returns) == 0:
        return {
            "annualized_return_pct": 0.0,
            "annualized_volatility_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe_ratio": 0.0,
            "observation_count": len(daily_prices)
        }

    # Mean daily return and annualized return (geometric / compound)
    total_return = (prices[-1] / prices[0]) - 1.0
    trading_days = len(returns)
    years = max(trading_days / 252.0, 1.0 / 252.0)
    ann_return = ((1.0 + total_return) ** (1.0 / years)) - 1.0 if (1.0 + total_return) > 0 else -1.0

    # Annualized Volatility
    daily_std = float(np.std(returns, ddof=1)) if len(returns) > 1 else 0.0
    ann_volatility = daily_std * math.sqrt(252.0)

    # Maximum Drawdown
    running_max = np.maximum.accumulate(prices)
    drawdowns = (prices - running_max) / running_max
    max_drawdown = float(np.min(drawdowns)) # e.g. -0.25 for -25%

    # Sharpe ratio
    if ann_volatility > 0.0:
        sharpe = (ann_return - annual_risk_free_rate) / ann_volatility
    else:
        sharpe = 0.0

    return {
        "annualized_return_pct": round(ann_return * 100.0, 2),
        "annualized_volatility_pct": round(ann_volatility * 100.0, 2),
        "max_drawdown_pct": round(max_drawdown * 100.0, 2),
        "sharpe_ratio": round(sharpe, 2),
        "observation_count": len(daily_prices)
    }


def simulate_portfolio_stress_scenarios(
    asset_class_allocation: Dict[str, float],
    total_portfolio_value: Decimal
) -> List[Dict[str, Any]]:
    """
    Stress test portfolio against documented historical market shocks:
    1. 2008 Global Financial Crisis: Equities -37%, Bonds +20%, Gold +5%, Crypto N/A, Cash 0%
    2. 2020 COVID-19 Flash Crash: Equities -20%, Bonds +8%, Gold +2%, Crypto -35%, Cash 0%
    3. 2022 Tech/Inflation Rate-Hike Sell-off: Equities -25%, Bonds -15%, Gold -1%, Crypto -65%, Cash 0%
    """
    val = float(to_decimal(total_portfolio_value))
    alloc = {k.lower(): v / 100.0 for k, v in asset_class_allocation.items()}

    scenarios = [
        {
            "name": "2008 Global Financial Crisis",
            "shocks": {"equity": -0.37, "mutual_fund": -0.35, "bond": 0.20, "gold": 0.05, "crypto": -0.50, "cash_equivalent": 0.0},
            "description": "Severe equity contraction with flight-to-safety bond surge and steady gold."
        },
        {
            "name": "2020 COVID-19 Liquidity Shock",
            "shocks": {"equity": -0.20, "mutual_fund": -0.18, "bond": 0.08, "gold": 0.02, "crypto": -0.35, "cash_equivalent": 0.0},
            "description": "Rapid market downturn across risk assets with treasury bond protection."
        },
        {
            "name": "2022 Stagflation & Rate-Hike Shock",
            "shocks": {"equity": -0.25, "mutual_fund": -0.22, "bond": -0.15, "gold": -0.01, "crypto": -0.65, "cash_equivalent": 0.0},
            "description": "Simultaneous drawdown in stocks and long-duration bonds during rising rates."
        }
    ]

    results = []
    for s in scenarios:
        shocks = s["shocks"]
        total_shock_pct = sum((alloc.get(ac, 0.0) * shocks.get(ac, 0.0) for ac in alloc))
        projected_value = val * (1.0 + total_shock_pct)
        dollar_impact = projected_value - val

        results.append({
            "scenario_name": s["name"],
            "description": s["description"],
            "estimated_impact_pct": round(total_shock_pct * 100.0, 2),
            "estimated_dollar_impact": to_decimal(Decimal(str(round(dollar_impact, 2)))),
            "projected_portfolio_value": to_decimal(Decimal(str(round(projected_value, 2))))
        })

    return results
