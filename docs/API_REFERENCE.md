# WealthOS AI — REST API Reference

All API routes are served under `/api/v1/` and return standard JSON payloads. All protected endpoints require an `Authorization: Bearer <jwt_token>` header.

## 1. Authentication & User Profile

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user account | No |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT bearer token | No |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Yes |
| `PUT` | `/api/v1/auth/settings` | Update user currency, income, and preferences | Yes |
| `GET` | `/api/v1/users/export-data` | Export full user account data as JSON | Yes |
| `DELETE` | `/api/v1/users/me` | Permanently delete account and all records | Yes |

## 2. Smart Money Manager & Budgets

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/transactions/` | List and filter transactions (by type, category, date) | Yes |
| `POST` | `/api/v1/transactions/` | Create a transaction (with auto-categorization) | Yes |
| `DELETE` | `/api/v1/transactions/{id}` | Delete a transaction | Yes |
| `GET` | `/api/v1/transactions/summary` | Cash flow totals, net savings, savings rate | Yes |
| `POST` | `/api/v1/transactions/import/preview` | Preview CSV statement, report invalid & duplicate rows | Yes |
| `POST` | `/api/v1/transactions/import/commit` | Commit validated CSV rows to database | Yes |
| `GET` | `/api/v1/transactions/export/csv` | Download complete transaction ledger as CSV | Yes |
| `GET` | `/api/v1/budgets/overview` | Category limits, actual spending, overage alerts | Yes |
| `POST` | `/api/v1/budgets/` | Set or update monthly category budget limit | Yes |

## 3. Savings, Debts & Purchases

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/savings/goals` | List user savings goals with progress and on-track status | Yes |
| `POST` | `/api/v1/savings/goals` | Create a savings goal | Yes |
| `GET` | `/api/v1/savings/emergency-fund` | Emergency fund runway, target amount, gap analysis | Yes |
| `GET` | `/api/v1/debts/` | List debt liabilities | Yes |
| `POST` | `/api/v1/debts/` | Record a debt (credit card, auto loan, student loan) | Yes |
| `POST` | `/api/v1/debts/simulate` | Simulate Avalanche vs Snowball payoff strategies | Yes |
| `POST` | `/api/v1/purchases/evaluate` | Deterministic 5-scenario purchase evaluation | Yes |

## 4. Market Data & Portfolio Risk

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/market/quote/{symbol}` | Fetch live quote, asset class, and price history | Yes |
| `GET` | `/api/v1/market/asset-classes` | Educational overview of supported financial products | Yes |
| `GET` | `/api/v1/portfolio/` | List user investment portfolios | Yes |
| `POST` | `/api/v1/portfolio/` | Create an investment portfolio | Yes |
| `POST` | `/api/v1/portfolio/{id}/holdings` | Add a holding with average buy price and market price | Yes |
| `GET` | `/api/v1/portfolio/{id}/risk-report` | Calculate HHI concentration, volatility, max drawdown, Sharpe, and stress tests | Yes |

## 5. Forecasting & Simulation

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/simulation/forecast-cashflow` | Chronological forecast with 80% confidence bands | Yes |
| `POST` | `/api/v1/simulation/project-wealth` | Compound wealth projection with inflation discount | Yes |
| `POST` | `/api/v1/simulation/monte-carlo` | 1,000-path Geometric Brownian Motion percentiles (P10-P90) | Yes |

## 6. AI Assistant, Learning, Scam & Decision Engine

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/assistant/chat` | Multi-turn conversational AI with deterministic tools | Yes |
| `GET` | `/api/v1/assistant/sessions` | List saved conversation sessions | Yes |
| `POST` | `/api/v1/knowledge/search` | Search verified financial knowledge docs via RAG | Yes |
| `GET` | `/api/v1/learning/topics` | List curriculum topics and user completion status | Yes |
| `GET` | `/api/v1/learning/topics/{id}` | Get lesson content and interactive quiz questions | Yes |
| `POST` | `/api/v1/learning/quiz/submit` | Grade quiz submission and update progress | Yes |
| `POST` | `/api/v1/scam/analyze` | Scan pitch for red flags, phishing, and Ponzi indicators | Yes |
| `GET` | `/api/v1/reports/health` | Transparent 7-factor Financial Health Score (0-100) | Yes |
| `GET` | `/api/v1/decision/overview` | Unified multi-pillar dashboard status | Yes |
| `POST` | `/api/v1/decision/evaluate` | Unified cross-module purchase and cashflow evaluation | Yes |
