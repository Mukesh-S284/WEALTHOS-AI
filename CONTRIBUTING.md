# Contributing to WealthOS AI

Thank you for your interest in contributing to **WealthOS AI**.

WealthOS AI is a production-grade personal finance, investment intelligence, and wealth planning platform. To preserve engineering integrity, all contributions must adhere to the following standards.

## 1. Non-Negotiable Development Rules

1. **Build Real Functionality:**
   - Every visible control must perform its real intended action.
   - All user data must persist in the database.
   - Do not implement fake login, fake uploads, fake charts, placeholder API responses, or synthetic mock values presented as real.
   - Never fabricate market prices, financial news, or model metrics.

2. **Decimal-Safe Monetary Arithmetic:**
   - Never use floating-point types (`float`) for currency or financial amounts in backend services and database models.
   - Always use `decimal.Decimal` with explicit rounding modes (`ROUND_HALF_UP`).

3. **Multi-Tenant Data Isolation:**
   - All new database models must include a `user_id` foreign key referencing `users.id` with `ondelete="CASCADE"`.
   - All query logic must strictly filter by `current_user.id`.

4. **Preserve Test Coverage:**
   - Write automated pytest tests for every new feature, calculation function, and API endpoint.
   - Never mark a feature complete unless its automated tests pass.

## 2. Local Development Setup

### 2.1 Prerequisites
- Python 3.10+ (Tested on Python 3.11 and 3.13)
- Git
- Virtual environment tool (`venv`)

### 2.2 Setup Steps
```bash
# Clone the repository
git clone https://github.com/wealthos-ai/wealthos-ai.git
cd wealthos-ai

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed initial demo financial data
python scripts/seed_demo_data.py

# Launch development backend & frontend
python scripts/run_app.py
```

## 3. Running Automated Tests

Run the complete test suite across unit, API, security, and end-to-end integration tests:

```bash
python -m pytest tests/ -v
```

All 82+ tests must pass before submitting a pull request.
