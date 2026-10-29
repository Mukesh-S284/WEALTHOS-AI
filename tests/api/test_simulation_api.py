"""API tests for Forecasting and Wealth Simulation endpoints."""

def test_cashflow_forecast_api(client, auth_headers):
    resp = client.get("/api/v1/simulation/cashflow-forecast?horizon_months=12", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["forecast_horizon_months"] == 12
    assert len(data["projections"]) == 12
    assert "projected_income" in data["projections"][0]
    assert "projected_expenses" in data["projections"][0]
    assert "projected_net_savings" in data["projections"][0]


def test_wealth_projection_api(client, auth_headers):
    payload = {
        "initial_balance": "25000.00",
        "monthly_contribution": "1200.00",
        "annual_return_pct": "7.5",
        "annual_inflation_pct": "2.8",
        "years": 15,
        "annual_contribution_step_up_pct": "3.0"
    }
    resp = client.post("/api/v1/simulation/wealth-projection", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["final_nominal_wealth"] > data["total_principal_invested"]
    assert len(data["yearly_trajectory"]) == 15


def test_monte_carlo_simulation_api(client, auth_headers):
    payload = {
        "initial_wealth": "30000.00",
        "monthly_contribution": "800.00",
        "expected_annual_return_pct": "8.5",
        "annual_volatility_pct": "15.0",
        "years": 10,
        "num_simulations": 300,
        "target_wealth": "200000.00",
        "random_seed": 101
    }
    resp = client.post("/api/v1/simulation/monte-carlo", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "probability_of_reaching_target_pct" in data
    assert "final_outcomes" in data
    assert "yearly_percentiles" in data
    assert len(data["yearly_percentiles"]) == 11
    assert "disclaimer" in data
