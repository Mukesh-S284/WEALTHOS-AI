"""API tests for Savings Goals and Emergency Fund endpoints."""

def test_create_and_contribute_savings_goal(client, auth_headers):
    # Create goal
    payload = {
        "title": "Emergency Reserve",
        "target_amount": "12000.00",
        "current_amount": "2000.00",
        "target_date": "2027-10-01",
        "monthly_contribution": "500.00",
        "priority": "critical",
        "category": "emergency_fund",
        "currency": "USD"
    }
    resp = client.post("/api/v1/savings/goals", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    goal = resp.json()
    assert goal["title"] == "Emergency Reserve"
    assert goal["current_amount"] == "2000.00"
    assert "required_monthly_savings" in goal
    goal_id = goal["id"]

    # Contribute 1000.00
    contrib_resp = client.post(
        f"/api/v1/savings/goals/{goal_id}/contribute",
        json={"amount": "1000.00", "notes": "Bonus deposit"},
        headers=auth_headers
    )
    assert contrib_resp.status_code == 200
    updated_goal = contrib_resp.json()
    assert updated_goal["current_amount"] == "3000.00"


def test_emergency_fund_endpoint(client, auth_headers):
    resp = client.get("/api/v1/savings/emergency-fund?target_months=6", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "months_covered" in data
    assert "target_amount" in data
    assert "gap_amount" in data
    assert "health_status" in data
