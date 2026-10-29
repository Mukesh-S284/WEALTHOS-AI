"""API tests for Transaction CRUD, summary statistics, and CSV import/export."""

import io
from datetime import date


def test_create_income_transaction(client, auth_headers):
    payload = {
        "date": "2026-10-01",
        "description": "Tech Corp Monthly Salary Direct Dep",
        "amount": "5000.00",
        "type": "income",
        "category": "Salary",
        "currency": "USD",
        "is_recurring": True,
        "recurrence_interval": "monthly"
    }
    response = client.post("/api/v1/transactions/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "5000.00"
    assert data["type"] == "income"
    assert data["category"] == "Salary"
    assert data["is_recurring"] is True


def test_create_expense_with_auto_categorization(client, auth_headers):
    payload = {
        "date": "2026-10-02",
        "description": "WHOLE FOODS MARKET SOMA SAN FRANCISCO",
        "amount": "142.50",
        "type": "expense",
        "category": "Uncategorized",  # Should be classified automatically
        "currency": "USD"
    }
    response = client.post("/api/v1/transactions/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "142.50"
    assert data["category"] == "Groceries"
    assert data["classification_source"] in ("rule", "ml")


def test_list_and_filter_transactions(client, auth_headers):
    # Add two transactions
    client.post("/api/v1/transactions/", json={
        "date": "2026-10-05", "description": "Starbucks Coffee", "amount": "6.75",
        "type": "expense", "category": "Dining", "currency": "USD"
    }, headers=auth_headers)

    client.post("/api/v1/transactions/", json={
        "date": "2026-10-06", "description": "Target Superstore", "amount": "85.20",
        "type": "expense", "category": "Shopping", "currency": "USD"
    }, headers=auth_headers)

    # Filter by category
    resp = client.get("/api/v1/transactions/?category=Dining", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    assert all(i["category"] == "Dining" for i in items)


def test_transaction_summary(client, auth_headers):
    # Summary calculates income, expenses, and savings rate
    resp = client.get("/api/v1/transactions/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_income" in data
    assert "total_expenses" in data
    assert "net_savings" in data
    assert "savings_rate_pct" in data


def test_csv_preview_and_commit_workflow(client, auth_headers):
    csv_data = (
        "Date,Description,Amount,Type,Category\n"
        "2026-10-10,Safeway Grocery Store,95.40,expense,Groceries\n"
        "2026-10-11,Netflix Subscription,19.99,expense,Subscriptions\n"
        "invalid-date,Broken Line,abc,expense,Other\n"
    )
    files = {"file": ("test.csv", csv_data.encode("utf-8"), "text/csv")}
    
    # Preview
    preview_resp = client.post("/api/v1/transactions/csv-preview", files=files, headers=auth_headers)
    assert preview_resp.status_code == 200
    preview = preview_resp.json()
    assert preview["total_rows"] == 3
    assert preview["valid_rows"] == 2
    assert preview["invalid_rows"] == 1
    assert len(preview["rows"][2]["errors"]) > 0

    # Commit valid rows
    valid_payload = [
        row["parsed_transaction"] for row in preview["rows"] if row["is_valid"]
    ]
    commit_resp = client.post(
        "/api/v1/transactions/csv-commit",
        json={"rows": valid_payload},
        headers=auth_headers
    )
    assert commit_resp.status_code == 201
    committed = commit_resp.json()
    assert len(committed) == 2


def test_export_transactions_csv(client, auth_headers):
    resp = client.get("/api/v1/transactions/export-csv", headers=auth_headers)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "Date,Description,Amount,Type,Category" in resp.text
