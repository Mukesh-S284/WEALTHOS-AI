"""API tests for Budget creation, tracking, and over-budget alerting."""

def test_set_and_get_budget(client, auth_headers):
    payload = {
        "category": "Groceries",
        "monthly_limit": "600.00",
        "currency": "USD",
        "period": "2026-10",
        "alert_threshold_percentage": "80.0"
    }
    create_resp = client.post("/api/v1/budgets/", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    budget_id = create_resp.json()["id"]

    get_resp = client.get(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["monthly_limit"] == "600.00"


def test_budget_overview_with_actual_spending(client, auth_headers):
    # Set Dining budget of 200.00
    client.post("/api/v1/budgets/", json={
        "category": "Dining",
        "monthly_limit": "200.00",
        "currency": "USD",
        "period": "2026-10",
        "alert_threshold_percentage": "80.0"
    }, headers=auth_headers)

    # Add expense of 170.00 in Dining -> 85% used (alert near limit)
    client.post("/api/v1/transactions/", json={
        "date": "2026-10-15",
        "description": "Fancy Dinner Out",
        "amount": "170.00",
        "type": "expense",
        "category": "Dining",
        "currency": "USD"
    }, headers=auth_headers)

    overview_resp = client.get("/api/v1/budgets/overview?period=2026-10", headers=auth_headers)
    assert overview_resp.status_code == 200
    overview = overview_resp.json()
    dining_item = next((i for i in overview["items"] if i["category"] == "Dining"), None)
    assert dining_item is not None
    assert dining_item["monthly_limit"] == "200.00"
    assert dining_item["spent_amount"] == "170.00"
    assert dining_item["remaining_amount"] == "30.00"
    assert dining_item["percentage_used"] == 85.0
    assert dining_item["is_near_limit"] is True
    assert dining_item["is_over_budget"] is False
