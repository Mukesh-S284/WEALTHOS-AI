"""API tests for Market Data and Portfolio Risk Analyzer endpoints."""

def test_get_asset_classes_educational(client, auth_headers):
    resp = client.get("/api/v1/market/asset-classes", headers=auth_headers)
    assert resp.status_code == 200
    classes = resp.json()
    assert len(classes) >= 5
    keys = [c["key"] for c in classes]
    assert "equity" in keys
    assert "bond" in keys
    assert "gold" in keys
    assert "crypto" in keys
    assert "cash_equivalent" in keys


def test_portfolio_lifecycle_and_risk_report(client, auth_headers):
    # 1. Create a Portfolio
    p_resp = client.post(
        "/api/v1/portfolios/",
        json={"name": "Retirement Growth", "description": "Long-term ETF allocation", "currency": "USD"},
        headers=auth_headers
    )
    assert p_resp.status_code == 201
    portfolio_id = p_resp.json()["id"]

    # 2. Add Stock holding
    h1 = client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={
            "symbol": "SPY", "name": "SPDR S&P 500 ETF", "asset_class": "equity",
            "quantity": "20.0", "average_buy_price": "450.00", "currency": "USD"
        },
        headers=auth_headers
    )
    assert h1.status_code == 201
    assert h1.json()["symbol"] == "SPY"

    # 3. Add Bond holding
    h2 = client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={
            "symbol": "BND", "name": "Vanguard Total Bond Market", "asset_class": "bond",
            "quantity": "50.0", "average_buy_price": "75.00", "currency": "USD"
        },
        headers=auth_headers
    )
    assert h2.status_code == 201

    # 4. Add Gold holding
    h3 = client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={
            "symbol": "GLD", "name": "SPDR Gold Trust", "asset_class": "gold",
            "quantity": "10.0", "average_buy_price": "180.00", "currency": "USD"
        },
        headers=auth_headers
    )
    assert h3.status_code == 201

    # 5. Fetch Portfolio details and verify valuation and allocation weights
    detail_resp = client.get(f"/api/v1/portfolios/{portfolio_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    p_data = detail_resp.json()
    assert len(p_data["holdings"]) == 3
    assert float(p_data["total_value"]) > 0
    assert "equity" in p_data["asset_class_allocation_pct"]
    assert "bond" in p_data["asset_class_allocation_pct"]
    assert "gold" in p_data["asset_class_allocation_pct"]

    # 6. Generate Risk Report
    risk_resp = client.get(f"/api/v1/portfolios/{portfolio_id}/risk-report", headers=auth_headers)
    assert risk_resp.status_code == 200
    risk = risk_resp.json()
    assert "annualized_volatility_pct" in risk
    assert "max_drawdown_pct" in risk
    assert "sharpe_ratio" in risk
    assert "concentration_hhi" in risk
    assert len(risk["stress_scenarios"]) == 3
    assert "disclaimer" in risk
