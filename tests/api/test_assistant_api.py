"""API tests for AI Financial Assistant and Knowledge endpoints."""

def test_assistant_chat_spending_intent(client, auth_headers):
    # Add an income and expense first
    client.post("/api/v1/transactions/", json={
        "date": "2026-10-01", "description": "Salary Paycheck", "amount": "4000.00",
        "type": "income", "category": "Salary", "currency": "USD"
    }, headers=auth_headers)
    client.post("/api/v1/transactions/", json={
        "date": "2026-10-02", "description": "Apartment Rent", "amount": "1500.00",
        "type": "expense", "category": "Housing", "currency": "USD"
    }, headers=auth_headers)

    # Ask assistant about spending
    payload = {"message": "Can you give me a summary of my spending and income?"}
    resp = client.post("/api/v1/assistant/chat", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "content" in data
    assert "$1,500.00" in data["content"] or "Expenses: $1,500.00" in data["content"]
    assert "tool_calls" in data
    assert any(tc["name"] == "get_financial_summary" for tc in data["tool_calls"])
    session_id = data["session_id"]

    # Verify session persists in list
    s_list = client.get("/api/v1/assistant/sessions", headers=auth_headers)
    assert s_list.status_code == 200
    assert any(s["id"] == session_id for s in s_list.json())


def test_knowledge_search_api(client, auth_headers):
    payload = {"query": "What is compound interest and SIP?", "top_k": 2}
    resp = client.post("/api/v1/knowledge/search", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_results"] >= 1
    assert any("Compound" in r["title"] or "SIP" in r["title"] for r in data["results"])
