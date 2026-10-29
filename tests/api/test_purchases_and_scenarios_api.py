"""API tests for Purchase Decisions and Life-Event Scenarios."""

def test_purchase_evaluation_api(client, auth_headers):
    payload = {
        "purchase_price": "2499.00",
        "available_liquid_savings": "7000.00",
        "monthly_net_surplus": "600.00",
        "minimum_cash_buffer": "3000.00",
        "financing_apr": "12.0",
        "financing_tenure_months": 12,
        "alternative_price": "1499.00"
    }
    resp = client.post("/api/v1/purchases/evaluate", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "verdict" in data
    assert "scenarios" in data
    assert "buy_now_cash" in data["scenarios"]
    assert "wait_and_save" in data["scenarios"]
    assert "lower_cost_alternative" in data["scenarios"]
    assert "financing" in data["scenarios"]


def test_life_event_scenario_api(client, auth_headers):
    payload = {
        "title": "Transition to Part-Time Consulting",
        "event_type": "job_transition",
        "monthly_income_delta": "-1500.00",
        "monthly_expense_delta": "200.00",
        "one_time_cost": "1000.00",
        "duration_months": 12,
        "notes": "Testing 12 months transition impact"
    }
    resp = client.post("/api/v1/scenarios/life-event?save=true", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == payload["title"]
    assert "net_wealth_impact" in data
    assert "is_sustainable" in data
    assert len(data["monthly_projections"]) == 12

    # Check that scenario was saved in list
    list_resp = client.get("/api/v1/scenarios/", headers=auth_headers)
    assert list_resp.status_code == 200
    saved = list_resp.json()
    assert len(saved) >= 1
    assert saved[0]["title"] == payload["title"]
