# WealthOS AI — Architectural Blueprint

## 1. System Overview

**WealthOS AI** is an explainable personal finance, investment intelligence, and wealth planning platform. The platform is architected around a **Unified Financial Decision Engine** ensuring that all modules (cash flow, debt payoff, liquidity buffers, investments, purchase evaluations, and simulations) operate on the same validated, deterministic financial data.

```
+---------------------------------------------------------------------------------+
|                                Streamlit Frontend                               |
| (14 Modules: Dashboard, Money Manager, Budgets, Savings, Portfolio, AI, etc.)  |
+----------------------------------------+----------------------------------------+
                                         | REST / JSON (HTTP)
                                         v
+---------------------------------------------------------------------------------+
|                                  FastAPI Layer                                  |
| (Pydantic v2 validation, JWT authentication, rate limiting, audit logging)      |
+-------------------+--------------------+-------------------+--------------------+
                    |                    |                   |
                    v                    v                   v
+-----------------------+ +----------------------+ +------------------------------+
| Deterministic Engine  | |   Machine Learning   | | AI Assistant & Knowledge     |
| - Cashflow & Budget   | | - Expense Classifier | | - Pure-Python RAG Retriever  |
| - Loan & Debt Payoff  | |   (Rules + TF-IDF LR)| | - Controlled Tool Registry   |
| - Portfolio Risk/HHI  | | - Forecasting Horizon| | - Gemini API / Local Fallback|
| - Monte Carlo GBM     | +----------------------+ +------------------------------+
+-----------------------+
                    |
                    v
+---------------------------------------------------------------------------------+
|                       Data Access Layer (SQLAlchemy 2.x)                        |
|   (PostgreSQL Production / SQLite In-Memory Testing with Foreign Key Isolation) |
+---------------------------------------------------------------------------------+
```

## 2. Layered Responsibilities

### 2.1 Presentation Layer (`frontend/`)
- Built with **Streamlit** and **Plotly**.
- Multi-page routing organized around 14 modules.
- Client communicates with FastAPI backend via `APIClient` (`frontend/services/api_client.py`).
- Session state preserves bearer tokens, authenticated profile info, and conversation turns.
- Clean fintech styling with responsive metrics, progress indicators, radar profiles, and waterfall graphs.

### 2.2 Application Services & API (`backend/`)
- **FastAPI** with structured routers mounted under `/api/v1/`.
- Strict input/output validation with **Pydantic v2**.
- Decimals (`decimal.Decimal`) are enforced for all monetary calculations to eliminate floating-point precision loss.
- Centralized exception handler catches `WealthOSException` and sanitizes unexpected 500 errors so sensitive database stack traces never leak to clients.

### 2.3 Deterministic Financial Engine (`finance_engine/`)
- Isolated, stateless calculation functions with zero external API dependencies.
- Submodules:
  - `budgeting/`: Cashflow summaries, surplus, 50/30/20 compliance, period-over-period variance.
  - `savings/`: Amortization, required monthly contributions, linear and compound projections, emergency fund adequacy.
  - `purchases/`: Exact loan installment formulas ($PMT = P \cdot \frac{r(1+r)^n}{(1+r)^n - 1}$), 5-scenario evaluation, liquidity buffer depletion, rebuild timelines.
  - `debt/`: Avalanche (highest APR first) vs Snowball (lowest balance first) payoff engines with total interest comparison.
  - `portfolio/`: Holding weights, HHI concentration, annualized standard deviation ($\sigma = \sqrt{252} \cdot \text{std}(R)$), maximum drawdown, Sharpe ratio, and crisis stress testing.
  - `simulation/`: Compound wealth growth, inflation adjustments, annual contribution step-up, and Geometric Brownian Motion (GBM) Monte Carlo engine.

### 2.4 AI and Machine Learning (`ml/` & `ai/`)
- **Expense Classification:** Hybrid architecture. Fast, deterministic regex rules for 95%+ precision across core merchant categories; TF-IDF + Logistic Regression fallback trained on transaction patterns (`ml/artifacts/expense_classifier.joblib`).
- **Knowledge Retrieval (RAG):** Self-contained pure-Python vector store (`ai/retrieval/vector_store.py`) computing TF-IDF subword n-gram cosine similarity over verified regulatory and educational docs.
- **Controlled Tool Registry:** Assistant does not compute finances using generative LLM weights; it calls validated deterministic python tools with Pydantic arguments (`ai/tools/registry.py`).
- **Prompt Injection Defense:** Input and retrieved context are scrubbed using `sanitize_retrieved_text` to neutralize prompt escape tokens and instruction override delimiters.

### 2.5 Multi-Tenant Database Architecture (`backend/models/`)
- Database migrations managed by **Alembic**.
- Every sensitive table (`transactions`, `budgets`, `savings_goals`, `debts`, `portfolios`, `portfolio_holdings`, `learning_progress`, `assistant_sessions`, `audit_logs`) enforces a mandatory `user_id` foreign key.
- Security tests confirm that user A can never read, modify, or delete user B's records.
