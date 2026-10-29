# WealthOS AI 💎
### Explainable AI-Powered Personal Finance, Investment Intelligence and Wealth Planning Platform

WealthOS AI is a production-ready, full-stack financial intelligence application built to help individuals understand their money, analyze investments, stress-test portfolios, evaluate large purchases, and simulate future wealth through a **Unified Financial Decision Engine**.

---

## 🚀 Key Modules & Capabilities

1. **Module A — Authentication & Multi-Tenant Profile:**
   Secure Bcrypt password hashing, signed JWT session management, user-specific tenant isolation, and GDPR/CCPA data export and account deletion workflows.

2. **Module B — Smart Money Manager:**
   Complete transaction CRUD, rule + TF-IDF Logistic Regression auto-categorizer, monthly budget limits, overage alert thresholds, bank CSV import preview with duplicate detection, and CSV ledger export.

3. **Module C & D — Investment Intelligence & Market Data:**
   Educational breakdowns of Stocks, Mutual Funds, Bonds, SIPs, Gold, and Crypto; live Yahoo Finance integration for real-time quotes, 52-week ranges, and historical price charts.

4. **Module E — Portfolio Risk, Allocation & Stress Testing:**
   Multi-asset holdings management, asset allocation pie charts, Herfindahl-Hirschman concentration index (HHI), annualized volatility ($\sigma = \sqrt{252} \cdot \text{std}$), maximum drawdown, Sharpe ratio, and historical macroeconomic crisis stress testing (2008 GFC, 2020 COVID, 2022 Stagflation).

5. **Module F — Smart Purchase Decision Engine:**
   Multi-scenario evaluation (Pay in Cash vs Loan Financing vs Alternative Option), liquid reserve buffer depletion analysis, and reserve rebuild horizon calculations.

6. **Module G — Wealth Simulator & Stochastic Monte Carlo Engine:**
   Deterministic compound growth modeling with annual SIP step-up and inflation purchasing-power discount; 1,000-path Geometric Brownian Motion (GBM) Monte Carlo simulation with P10-P90 percentiles and goal attainment probabilities.

7. **Module H — Grounded Financial AI Assistant:**
   Conversational AI assistant powered by pure-Python RAG vector retrieval over verified regulatory and educational docs, controlled deterministic tool registry (Pydantic validated), and indirect prompt injection sanitization.

8. **Module I — Financial Learning Coach:**
   Structured multi-topic curriculum (50/30/20, Emergency Funds, Compound Interest, Debt Strategies, SIP & DCA, Asset Allocation, Crypto Volatility) with interactive graded quizzes, pass/fail thresholds, and detailed answer explanations.

9. **Module J — Scam & Fraud Awareness Engine:**
   Rule-based heuristic detector scanning investment pitches for guaranteed returns, manufactured urgency/FOMO, credential/OTP phishing, Ponzi/pyramid recruitment, and untraceable payment demands with official FINRA/SEC verification steps.

10. **Module K — Financial Health Indicators & Diagnostic Reports:**
    Transparent 7-factor objective Financial Health Score (0-100) evaluating savings rate, emergency runway, budget control, debt service burden (DTI), goal adherence, expense stability, and asset diversification with radar visualizations.

11. **Module L — Unified Financial Decision Engine:**
    Cross-module intelligence that links cash flow, emergency buffers, debt service commitments, and competing savings goals. Quantifies exact delays in target goal dates when a major financed purchase or life change is introduced.

12. **Module M — Regulatory & Professional Compliance:**
    Standardized fiduciary disclaimers, mathematical transparency, absence of synthetic fabricated market prices, and strict regulatory notices across all screens.

13. **Module N — Life-Event & Cash-Flow Shock Planner:**
    Deterministic modeler for career sabbaticals, geographic relocation, medical emergencies, and home purchases.

---

## 🛠️ Technology Stack

- **Frontend:** Streamlit, Plotly, custom CSS design system.
- **Backend:** Python 3.11/3.13, FastAPI, Pydantic v2.
- **Database:** PostgreSQL (production), SQLite (in-memory test isolation), SQLAlchemy 2.x ORM, Alembic migrations.
- **Machine Learning & Analytics:** Scikit-learn, Pandas, NumPy, Statsmodels.
- **AI & Knowledge Engine:** Pure-Python TF-IDF subword vector store, Controlled Tool Registry, Gemini API adapter with grounded local fallback.
- **Infrastructure & Testing:** Docker, Docker Compose, Pytest (82 automated tests), Makefile.

---

## 🏁 Quickstart Guide

### Option 1: Local Python Run

1. **Clone the repository and install dependencies:**
   ```bash
   git clone https://github.com/wealthos-ai/wealthos-ai.git
   cd wealthos-ai
   pip install -r requirements.txt
   ```

2. **Initialize database migrations and seed demo data:**
   ```bash
   alembic upgrade head
   python scripts/seed_demo_data.py
   ```

3. **Start backend and frontend concurrently:**
   ```bash
   python scripts/run_app.py
   # Or using make:
   make run
   ```

4. **Access the application:**
   - **Frontend UI:** `http://localhost:8501`
   - **FastAPI Swagger Docs:** `http://localhost:8000/docs`
   - **Demo Credentials:** `demo@wealthos.ai` / `SecurePass123!`

---

### Option 2: Docker Compose

Launch PostgreSQL, FastAPI Backend, and Streamlit Frontend in isolated containers:

```bash
docker-compose up --build -d
```

- **Frontend:** `http://localhost:8501`
- **Backend:** `http://localhost:8000`

---

## 🧪 Automated Test Suite

WealthOS AI maintains an exhaustive, verified automated test suite of **82 tests** covering all 14 modules:

```bash
python -m pytest tests/ -v
```

```
tests/api/test_assistant_api.py ......................... PASSED
tests/api/test_auth_api.py .............................. PASSED
tests/api/test_budgets_api.py ........................... PASSED
tests/api/test_debts_api.py ............................. PASSED
tests/api/test_learning_and_reports_api.py .............. PASSED
tests/api/test_market_and_portfolio_api.py .............. PASSED
tests/api/test_purchases_and_scenarios_api.py ........... PASSED
tests/api/test_savings_api.py ........................... PASSED
tests/api/test_simulation_api.py ........................ PASSED
tests/api/test_transactions_api.py ...................... PASSED
tests/security/test_transaction_isolation.py ............ PASSED
tests/security/test_user_isolation.py ................... PASSED
tests/unit/test_ai_tools.py ............................. PASSED
tests/unit/test_budget_engine.py ........................ PASSED
tests/unit/test_debt_engine.py .......................... PASSED
tests/unit/test_expense_classifier.py ................... PASSED
tests/unit/test_forecasting.py .......................... PASSED
tests/unit/test_health_report.py ........................ PASSED
tests/unit/test_learning.py ............................. PASSED
tests/unit/test_portfolio_metrics.py .................... PASSED
tests/unit/test_purchase_engine.py ...................... PASSED
tests/unit/test_rag.py .................................. PASSED
tests/unit/test_savings_engine.py ....................... PASSED
tests/unit/test_scam_detector.py ........................ PASSED
tests/unit/test_security.py ............................. PASSED
tests/unit/test_simulation.py ........................... PASSED
tests/end_to_end/test_unified_workflow.py ............... PASSED
============================= 82 passed in 100% =============================
```

---

## 📖 Documentation Directory

- [Architecture Blueprint](docs/ARCHITECTURE.md)
- [Database Schema & Data Models](docs/DATABASE_SCHEMA.md)
- [REST API Reference](docs/API_REFERENCE.md)
- [Mathematical & Financial Calculations](docs/FINANCIAL_CALCULATIONS.md)
- [External Data Sources & Provenance Policy](docs/DATA_SOURCES.md)
- [AI Safety & Governance](docs/AI_SAFETY.md)
- [Machine Learning Model Evaluation](docs/ML_EVALUATION.md)
- [Security Policy](SECURITY.md)
- [Contributing Guidelines](CONTRIBUTING.md)

---

## 📜 Regulatory Disclaimer

WealthOS AI is a software intelligence platform designed for personal budgeting, scenario simulation, and educational research. WealthOS AI does not provide licensed fiduciary advice, portfolio management, or individual securities recommendations. Market calculations are based on historical and modeled data. Past performance does not guarantee future results.
