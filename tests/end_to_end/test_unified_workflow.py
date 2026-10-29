"""End-to-End integration tests for Unified Financial Decision Engine and cross-module workflows."""

from decimal import Decimal
from datetime import date


def test_unified_financial_lifecycle_and_decision_engine(client, auth_headers):
    # 1. Establish baseline income and expenses
    resp_inc = client.post("/api/v1/transactions/", json={
        "date": "2026-10-01",
        "description": "Tech Corp Monthly Salary",
        "amount": "6000.00",
        "type": "income",
        "category": "Salary",
        "currency": "USD"
    }, headers=auth_headers)
    assert resp_inc.status_code == 201

    resp_exp1 = client.post("/api/v1/transactions/", json={
        "date": "2026-10-02",
        "description": "Apartment Rent",
        "amount": "1800.00",
        "type": "expense",
        "category": "Housing",
        "currency": "USD"
    }, headers=auth_headers)
    assert resp_exp1.status_code == 201

    resp_exp2 = client.post("/api/v1/transactions/", json={
        "date": "2026-10-05",
        "description": "Organic Supermarket Groceries",
        "amount": "600.00",
        "type": "expense",
        "category": "Groceries",
        "currency": "USD"
    }, headers=auth_headers)
    assert resp_exp2.status_code == 201

    # 2. Add an emergency fund goal and an active savings goal
    resp_ef = client.post("/api/v1/savings/goals", json={
        "title": "Emergency Liquid Reserve",
        "category": "emergency_fund",
        "target_amount": "15000.00",
        "current_amount": "12000.00",
        "target_date": "2027-12-31",
        "monthly_contribution": "300.00",
        "expected_annual_return_pct": "4.0"
    }, headers=auth_headers)
    assert resp_ef.status_code == 201

    resp_goal = client.post("/api/v1/savings/goals", json={
        "title": "Home Down Payment",
        "target_amount": "40000.00",
        "current_amount": "12000.00",
        "target_date": "2028-12-31",
        "monthly_contribution": "800.00",
        "expected_annual_return_pct": "6.0"
    }, headers=auth_headers)
    assert resp_goal.status_code == 201
    goal_id = resp_goal.json()["id"]

    # 3. Add an existing debt
    resp_debt = client.post("/api/v1/debts/", json={
        "name": "Student Loan",
        "debt_type": "student_loan",
        "principal_amount": "15000.00",
        "current_balance": "12000.00",
        "interest_rate_apr": "5.0",
        "minimum_monthly_payment": "250.00"
    }, headers=auth_headers)
    assert resp_debt.status_code == 201

    # 4. Verify Unified Overview aggregates all modules accurately
    resp_overview = client.get("/api/v1/decision/overview", headers=auth_headers)
    assert resp_overview.status_code == 200
    ov = resp_overview.json()
    assert float(ov["monthly_income"]) == 6000.00
    assert float(ov["monthly_expenses"]) == 2400.00
    assert float(ov["net_monthly_savings"]) == 3600.00
    assert ov["savings_rate_pct"] == 60.00
    assert float(ov["total_debt_balance"]) == 12000.00
    assert ov["active_goals_count"] >= 1
    assert 0 <= ov["health_score"] <= 100

    # 5. Evaluate Decision 1: Feasible Financed Purchase ($25,000 Car, $5,000 Down, 6.0% APR, 48 mos)
    payload_eval_feasible = {
        "decision_type": "expensive_purchase",
        "purchase": {
            "name": "Used Commuter Sedan",
            "cost": "25000.00",
            "financing_option": "loan",
            "down_payment": "5000.00",
            "loan_interest_rate_pct": "6.0",
            "loan_term_months": 48
        }
    }
    resp_dec1 = client.post("/api/v1/decision/evaluate", json=payload_eval_feasible, headers=auth_headers)
    assert resp_dec1.status_code == 200
    d1 = resp_dec1.json()
    assert d1["decision_type"] == "expensive_purchase"
    assert d1["is_recommended"] is True
    assert d1["recommendation_verdict"] in ("APPROVED_SAFE", "PROCEED_WITH_CAUTION")
    assert d1["budget_impact"]["is_cashflow_negative"] is False
    assert float(d1["budget_impact"]["monthly_surplus_after"]) > 0
    assert float(d1["debt_impact"]["total_monthly_debt_service_after"]) > 250.00
    assert len(d1["tradeoff_analysis"]) > 0

    # 6. Evaluate Decision 2: Extreme Unaffordable Purchase ($120,000 Sports Car, $0 Down, 10% APR, 36 mos)
    # Monthly loan payment for 120k at 10% for 36 mos is ~$3,872/mo, exceeding $3,600 surplus!
    payload_eval_unaffordable = {
        "decision_type": "expensive_purchase",
        "purchase": {
            "name": "Supercar",
            "cost": "120000.00",
            "financing_option": "loan",
            "down_payment": "0.00",
            "loan_interest_rate_pct": "10.0",
            "loan_term_months": 36
        }
    }
    resp_dec2 = client.post("/api/v1/decision/evaluate", json=payload_eval_unaffordable, headers=auth_headers)
    assert resp_dec2.status_code == 200
    d2 = resp_dec2.json()
    assert d2["is_recommended"] is False
    assert d2["recommendation_verdict"] == "NOT_RECOMMENDED"
    assert d2["budget_impact"]["is_cashflow_negative"] is True
    assert len(d2["actionable_alternatives"]) > 0
    assert d2["estimated_health_score_after"] < d2["health_score_before"]

    # 7. Evaluate Decision 3: Increasing Monthly SIP Investment ($400/month)
    payload_sip = {
        "decision_type": "increase_savings_sip",
        "additional_sip_amount": "400.00",
        "target_goal_id": goal_id
    }
    resp_dec3 = client.post("/api/v1/decision/evaluate", json=payload_sip, headers=auth_headers)
    assert resp_dec3.status_code == 200
    d3 = resp_dec3.json()
    assert d3["is_recommended"] is True
    assert d3["recommendation_verdict"] == "APPROVED_SAFE"
    assert float(d3["budget_impact"]["monthly_surplus_after"]) == 3200.00

    # 8. Evaluate Decision 4: Large Cash Purchase Depleting Emergency Fund
    payload_cash_drain = {
        "decision_type": "expensive_purchase",
        "purchase": {
            "name": "Luxury Watch",
            "cost": "11000.00",
            "financing_option": "cash"
        }
    }
    resp_dec4 = client.post("/api/v1/decision/evaluate", json=payload_cash_drain, headers=auth_headers)
    assert resp_dec4.status_code == 200
    d4 = resp_dec4.json()
    assert d4["emergency_fund_impact"]["months_depleted"] > 0
    assert d4["emergency_fund_impact"]["is_compromised"] is True
    assert d4["emergency_fund_impact"]["rebuild_months"] is not None
    assert d4["recommendation_verdict"] in ("PROCEED_WITH_CAUTION", "NOT_RECOMMENDED")

