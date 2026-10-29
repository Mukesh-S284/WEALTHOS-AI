"""API tests for Debts and Payoff simulation endpoints."""

def test_debt_crud_and_simulation(client, auth_headers):
    # Create Debt 1
    d1_payload = {
        "name": "High Interest Credit Card",
        "debt_type": "credit_card",
        "principal_amount": "4000.00",
        "current_balance": "4000.00",
        "interest_rate_apr": "24.5",
        "minimum_monthly_payment": "120.00",
        "currency": "USD"
    }
    r1 = client.post("/api/v1/debts/", json=d1_payload, headers=auth_headers)
    assert r1.status_code == 201
    d1_id = r1.json()["id"]

    # Create Debt 2
    d2_payload = {
        "name": "Personal Loan",
        "debt_type": "personal_loan",
        "principal_amount": "2000.00",
        "current_balance": "2000.00",
        "interest_rate_apr": "9.0",
        "minimum_monthly_payment": "75.00",
        "currency": "USD"
    }
    r2 = client.post("/api/v1/debts/", json=d2_payload, headers=auth_headers)
    assert r2.status_code == 201

    # Simulate Payoff
    sim_resp = client.post(
        "/api/v1/debts/simulate-payoff",
        json={"extra_monthly_payment": "150.00"},
        headers=auth_headers
    )
    assert sim_resp.status_code == 200
    sim = sim_resp.json()
    assert "avalanche" in sim
    assert "snowball" in sim
    assert sim["avalanche"]["total_months"] > 0
    assert "recommendation" in sim
