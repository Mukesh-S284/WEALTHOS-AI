"""Security tests for transaction and budget multi-tenant isolation."""

def test_cross_user_transaction_isolation(client, auth_headers, second_auth_headers):
    # User 1 creates transaction
    resp1 = client.post("/api/v1/transactions/", json={
        "date": "2026-10-01",
        "description": "User 1 Private Medical Bill",
        "amount": "350.00",
        "type": "expense",
        "category": "Healthcare",
        "currency": "USD"
    }, headers=auth_headers)
    assert resp1.status_code == 201
    user1_tx_id = resp1.json()["id"]

    # User 2 tries to GET User 1's transaction -> 404 Not Found
    resp_get = client.get(f"/api/v1/transactions/{user1_tx_id}", headers=second_auth_headers)
    assert resp_get.status_code == 404

    # User 2 tries to DELETE User 1's transaction -> 404 Not Found
    resp_del = client.delete(f"/api/v1/transactions/{user1_tx_id}", headers=second_auth_headers)
    assert resp_del.status_code == 404

    # User 2 lists transactions -> User 1 transaction is NOT visible in User 2's list
    resp_list = client.get("/api/v1/transactions/", headers=second_auth_headers)
    assert resp_list.status_code == 200
    user2_items = resp_list.json()
    assert all(i["id"] != user1_tx_id for i in user2_items)


def test_cross_user_budget_isolation(client, auth_headers, second_auth_headers):
    # User 1 creates budget
    resp1 = client.post("/api/v1/budgets/", json={
        "category": "Private Coaching",
        "monthly_limit": "500.00",
        "currency": "USD",
        "period": "2026-10"
    }, headers=auth_headers)
    assert resp1.status_code == 201
    user1_budget_id = resp1.json()["id"]

    # User 2 cannot get or delete User 1's budget
    resp_get = client.get(f"/api/v1/budgets/{user1_budget_id}", headers=second_auth_headers)
    assert resp_get.status_code == 404

    resp_del = client.delete(f"/api/v1/budgets/{user1_budget_id}", headers=second_auth_headers)
    assert resp_del.status_code == 404
