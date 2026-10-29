"""Unit tests for AI Assistant Tool Registry execution."""

from datetime import date
from ai.tools.registry import ToolRegistry


def test_tool_registry_definitions(db_session):
    registry = ToolRegistry(db_session)
    tools = registry.get_tool_definitions()
    names = [t["name"] for t in tools]

    assert "get_financial_summary" in names
    assert "calculate_savings_goal" in names
    assert "compare_purchase_scenarios" in names
    assert "calculate_debt_repayment" in names
    assert "simulate_future_savings" in names
    assert "retrieve_finance_knowledge" in names


def test_tool_execution_savings_and_purchase(db_session, test_user):
    registry = ToolRegistry(db_session)

    # Calculate savings goal tool
    savings_out = registry.execute_tool(
        test_user,
        "calculate_savings_goal",
        {"target_amount": 12000, "current_amount": 2000, "target_date": "2027-10-01"}
    )
    assert savings_out["shortfall"] == 10000.0
    assert savings_out["months_remaining"] > 0
    assert savings_out["required_monthly_contribution"] > 0.0

    # Compare purchase scenarios tool
    purchase_out = registry.execute_tool(
        test_user,
        "compare_purchase_scenarios",
        {"purchase_price": 1500, "available_savings": 6000, "monthly_surplus": 500, "minimum_buffer": 2000}
    )
    assert "verdict" in purchase_out
    assert purchase_out["cash_remaining_if_bought_now"] == 4500.0
    assert purchase_out["violates_buffer"] is False
