"""Controlled Tool Registry for the AI Financial Assistant."""

from typing import Dict, Any, Callable, List, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.models.user import User
from backend.services.transaction_service import TransactionService
from backend.services.portfolio_service import PortfolioService
from finance_engine.savings.engine import calculate_required_monthly_savings
from finance_engine.purchases.engine import evaluate_purchase_decision
from finance_engine.debt.engine import compare_debt_strategies
from finance_engine.simulation.wealth_projection import calculate_wealth_projection
from ai.retrieval.vector_store import RAGVectorStore


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters_schema: Dict[str, Any]


class ToolRegistry:
    """Central registry executing authorized financial tools on behalf of users."""

    def __init__(self, db: Session, rag_store: Optional[RAGVectorStore] = None):
        self.db = db
        self.rag_store = rag_store or RAGVectorStore()
        self.transaction_service = TransactionService(db)
        self.portfolio_service = PortfolioService(db)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return schema descriptions for all available assistant tools."""
        return [
            {
                "name": "get_financial_summary",
                "description": "Retrieve user's real total income, total expenses, net savings, and savings rate percentage.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "calculate_savings_goal",
                "description": "Calculate required monthly savings contribution to achieve a target amount by a specific date.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target_amount": {"type": "number", "description": "Target amount to accumulate"},
                        "current_amount": {"type": "number", "description": "Current savings already held"},
                        "target_date": {"type": "string", "description": "Target date in 'YYYY-MM-DD' format"},
                        "annual_return_pct": {"type": "number", "description": "Expected annual return (0 for cash)"}
                    },
                    "required": ["target_amount", "target_date"]
                }
            },
            {
                "name": "compare_purchase_scenarios",
                "description": "Evaluate purchase affordability, buffer depletion, rebuild time, and financing costs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "purchase_price": {"type": "number", "description": "Price of the item or expense"},
                        "available_savings": {"type": "number", "description": "Available cash savings"},
                        "monthly_surplus": {"type": "number", "description": "Net monthly cash surplus"},
                        "minimum_buffer": {"type": "number", "description": "Minimum emergency cash reserve"}
                    },
                    "required": ["purchase_price"]
                }
            },
            {
                "name": "calculate_debt_repayment",
                "description": "Compare Avalanche (highest APR first) vs Snowball (lowest balance first) debt payoff strategies.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "extra_monthly_payment": {"type": "number", "description": "Extra cash added to minimum debt payments"}
                    }
                }
            },
            {
                "name": "analyze_portfolio_risk",
                "description": "Analyze user's investment portfolio: asset allocation weights, concentration, volatility, and stress tests.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "portfolio_id": {"type": "string", "description": "Portfolio ID"}
                    }
                }
            },
            {
                "name": "simulate_future_savings",
                "description": "Project compound interest wealth accumulation with inflation adjustment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "initial_balance": {"type": "number", "description": "Starting principal balance"},
                        "monthly_contribution": {"type": "number", "description": "Monthly investment amount"},
                        "annual_return_pct": {"type": "number", "description": "Expected annual return percentage"},
                        "years": {"type": "integer", "description": "Number of years"}
                    },
                    "required": ["initial_balance", "monthly_contribution", "annual_return_pct", "years"]
                }
            },
            {
                "name": "retrieve_finance_knowledge",
                "description": "Retrieve official educational guidance and disclosures from verified publications (FINRA, SEC).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query or concept"}
                    },
                    "required": ["query"]
                }
            }
        ]

    def execute_tool(self, user: User, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool with strict server-side authorization and parameter validation."""
        if tool_name == "get_financial_summary":
            summary = self.transaction_service.get_summary(user)
            return {
                "total_income": float(summary.total_income),
                "total_expenses": float(summary.total_expenses),
                "net_savings": float(summary.net_savings),
                "savings_rate_pct": summary.savings_rate_pct,
                "currency": summary.currency,
                "transaction_count": summary.transaction_count
            }

        elif tool_name == "calculate_savings_goal":
            target = Decimal(str(arguments.get("target_amount", 0)))
            current = Decimal(str(arguments.get("current_amount", 0)))
            t_date = date.fromisoformat(arguments.get("target_date", date.today().isoformat()))
            ret_pct = Decimal(str(arguments.get("annual_return_pct", 0)))
            res = calculate_required_monthly_savings(
                target_amount=target,
                current_amount=current,
                target_date=t_date,
                annual_return_pct=ret_pct
            )
            return {
                "required_monthly_contribution": float(res["required_monthly_contribution"]),
                "months_remaining": res["months_remaining"],
                "shortfall": float(res["shortfall"]),
                "is_completed": res["is_completed"],
                "is_overdue": res["is_overdue"]
            }

        elif tool_name == "compare_purchase_scenarios":
            price = Decimal(str(arguments.get("purchase_price", 0)))
            savings = Decimal(str(arguments.get("available_savings", 5000)))
            surplus = Decimal(str(arguments.get("monthly_surplus", 800)))
            buffer = Decimal(str(arguments.get("minimum_buffer", 3000)))
            res = evaluate_purchase_decision(
                purchase_price=price,
                available_liquid_savings=savings,
                monthly_net_surplus=surplus,
                minimum_cash_buffer=buffer
            )
            return {
                "verdict": res["verdict"],
                "verdict_summary": res["verdict_summary"],
                "cash_remaining_if_bought_now": float(res["scenarios"]["buy_now_cash"]["cash_remaining"]),
                "violates_buffer": res["scenarios"]["buy_now_cash"]["violates_buffer"],
                "months_to_rebuild_buffer": res["scenarios"]["buy_now_cash"]["months_to_rebuild_buffer"],
                "months_to_wait_and_save": res["scenarios"]["wait_and_save"]["months_to_save"]
            }

        elif tool_name == "calculate_debt_repayment":
            from backend.services.debt_service import DebtService
            ds = DebtService(self.db)
            extra = Decimal(str(arguments.get("extra_monthly_payment", 0)))
            sim = ds.simulate_payoff(user, extra_payment=extra)
            return {
                "avalanche_months": sim.avalanche.total_months,
                "avalanche_interest_paid": float(sim.avalanche.total_interest_paid),
                "snowball_months": sim.snowball.total_months,
                "snowball_interest_paid": float(sim.snowball.total_interest_paid),
                "interest_savings": float(sim.avalanche_interest_savings),
                "recommendation": sim.recommendation
            }

        elif tool_name == "analyze_portfolio_risk":
            portfolios = self.portfolio_service.list_portfolios(user)
            if not portfolios:
                return {"message": "User has no investment portfolios created."}
            pid = arguments.get("portfolio_id") or portfolios[0].id
            report = self.portfolio_service.generate_risk_report(user, pid)
            return {
                "portfolio_name": report.portfolio_name,
                "total_value": float(report.total_value),
                "asset_class_allocation": report.asset_class_allocation,
                "annualized_volatility_pct": report.annualized_volatility_pct,
                "max_drawdown_pct": report.max_drawdown_pct,
                "sharpe_ratio": report.sharpe_ratio,
                "risk_level_assessment": report.risk_level_assessment
            }

        elif tool_name == "simulate_future_savings":
            init_b = Decimal(str(arguments.get("initial_balance", 0)))
            pmt = Decimal(str(arguments.get("monthly_contribution", 0)))
            ret_pct = Decimal(str(arguments.get("annual_return_pct", 7.0)))
            years = int(arguments.get("years", 10))
            sim = calculate_wealth_projection(
                initial_balance=init_b,
                monthly_contribution=pmt,
                annual_return_pct=ret_pct,
                years=years
            )
            return {
                "final_nominal_wealth": sim["final_nominal_wealth"],
                "final_real_purchasing_power": sim["final_real_purchasing_power"],
                "total_principal_invested": sim["total_principal_invested"],
                "total_compound_gains": sim["total_compound_gains"]
            }

        elif tool_name == "retrieve_finance_knowledge":
            query = str(arguments.get("query", ""))
            chunks = self.rag_store.search(query, top_k=2)
            return {
                "query": query,
                "results_count": len(chunks),
                "citations": [
                    {
                        "title": c["title"],
                        "publisher": c["publisher"],
                        "date": c["publication_date"],
                        "excerpt": c["content"][:300] + "..."
                    }
                    for c in chunks
                ]
            }

        raise ValueError(f"Unknown tool: '{tool_name}'")
