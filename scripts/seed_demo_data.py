"""Seed script for WealthOS AI: initializes a demo user and realistic financial records."""

import sys
from pathlib import Path
from datetime import date, datetime, timezone
from decimal import Decimal

# Ensure project root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.core.database import SessionLocal, Base, engine
import backend.models  # load all models into Base.metadata
from backend.core.security import hash_password
from backend.models.user import User
from backend.models.transaction import Transaction
from backend.models.budget import Budget
from backend.models.savings import SavingsGoal
from backend.models.debt import Debt
from backend.models.portfolio import Portfolio, PortfolioHolding
from backend.models.learning import LearningProgress


def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Create or retrieve demo user
        demo_email = "demo@wealthos.ai"
        user = db.query(User).filter(User.email == demo_email).first()
        if not user:
            user = User(
                email=demo_email,
                hashed_password=hash_password("SecurePass123!"),
                full_name="Alex Morgan",
                preferred_currency="USD",
                monthly_income="7500.00",
                timezone="America/New_York"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo user: {demo_email} (Password: SecurePass123!)")
        else:
            print(f"Demo user already exists: {demo_email}")

        # 2. Add realistic transactions if user has none
        tx_count = db.query(Transaction).filter(Transaction.user_id == user.id).count()
        if tx_count == 0:
            transactions = [
                # Incomes
                Transaction(user_id=user.id, date=date(2026, 10, 1), amount=Decimal("7500.00"), type="income", category="Salary", description="Senior Software Engineer Paycheck", is_recurring=True),
                Transaction(user_id=user.id, date=date(2026, 10, 15), amount=Decimal("450.00"), type="income", category="Investments", description="Quarterly ETF Dividend Distribution"),
                
                # Housing & Utilities
                Transaction(user_id=user.id, date=date(2026, 10, 2), amount=Decimal("2200.00"), type="expense", category="Housing", description="Downtown Loft Rental Payment", is_recurring=True),
                Transaction(user_id=user.id, date=date(2026, 10, 3), amount=Decimal("180.00"), type="expense", category="Utilities", description="City Power & Clean Water", is_recurring=True),
                Transaction(user_id=user.id, date=date(2026, 10, 4), amount=Decimal("85.00"), type="expense", category="Utilities", description="Fiber Gigabit Internet Service", is_recurring=True),

                # Groceries & Food
                Transaction(user_id=user.id, date=date(2026, 10, 5), amount=Decimal("142.50"), type="expense", category="Groceries", description="Whole Foods Organic Market"),
                Transaction(user_id=user.id, date=date(2026, 10, 12), amount=Decimal("118.20"), type="expense", category="Groceries", description="Trader Joe's Weekly Groceries"),
                Transaction(user_id=user.id, date=date(2026, 10, 19), amount=Decimal("135.00"), type="expense", category="Groceries", description="Sprouts Farmers Market"),
                Transaction(user_id=user.id, date=date(2026, 10, 7), amount=Decimal("65.00"), type="expense", category="Dining Out", description="Bistro Sushi Dinner"),
                Transaction(user_id=user.id, date=date(2026, 10, 16), amount=Decimal("42.50"), type="expense", category="Dining Out", description="Artisan Pizzeria & Drinks"),

                # Transportation & Fuel
                Transaction(user_id=user.id, date=date(2026, 10, 6), amount=Decimal("55.00"), type="expense", category="Transportation", description="Chevron Gasoline Station"),
                Transaction(user_id=user.id, date=date(2026, 10, 18), amount=Decimal("52.00"), type="expense", category="Transportation", description="Shell Gasoline Refuel"),

                # Health & Fitness
                Transaction(user_id=user.id, date=date(2026, 10, 8), amount=Decimal("120.00"), type="expense", category="Healthcare", description="Equinox Fitness Membership", is_recurring=True),

                # Entertainment & Subscriptions
                Transaction(user_id=user.id, date=date(2026, 10, 9), amount=Decimal("19.99"), type="expense", category="Entertainment", description="Netflix Premium UHD", is_recurring=True),
                Transaction(user_id=user.id, date=date(2026, 10, 10), amount=Decimal("11.99"), type="expense", category="Entertainment", description="Spotify Family Plan", is_recurring=True)
            ]
            db.add_all(transactions)
            db.commit()
            print(f"Seeded {len(transactions)} realistic transactions.")

        # 3. Add Budgets
        b_count = db.query(Budget).filter(Budget.user_id == user.id).count()
        if b_count == 0:
            budgets = [
                Budget(user_id=user.id, category="Housing", monthly_limit=Decimal("2300.00"), period="2026-10"),
                Budget(user_id=user.id, category="Groceries", monthly_limit=Decimal("600.00"), period="2026-10"),
                Budget(user_id=user.id, category="Dining Out", monthly_limit=Decimal("250.00"), period="2026-10"),
                Budget(user_id=user.id, category="Utilities", monthly_limit=Decimal("350.00"), period="2026-10"),
                Budget(user_id=user.id, category="Transportation", monthly_limit=Decimal("200.00"), period="2026-10"),
                Budget(user_id=user.id, category="Healthcare", monthly_limit=Decimal("200.00"), period="2026-10"),
                Budget(user_id=user.id, category="Entertainment", monthly_limit=Decimal("150.00"), period="2026-10")
            ]
            db.add_all(budgets)
            db.commit()
            print(f"Seeded {len(budgets)} category budgets for 2026-10.")

        # 4. Add Savings Goals (Emergency Fund and Home Down Payment)
        g_count = db.query(SavingsGoal).filter(SavingsGoal.user_id == user.id).count()
        if g_count == 0:
            goals = [
                SavingsGoal(
                    user_id=user.id,
                    title="Liquid Emergency Cushion",
                    category="emergency_fund",
                    target_amount=Decimal("20000.00"),
                    current_amount=Decimal("18000.00"),
                    target_date=date(2027, 6, 30),
                    monthly_contribution=Decimal("500.00"),
                    expected_annual_return_pct=Decimal("4.5")
                ),
                SavingsGoal(
                    user_id=user.id,
                    title="Real Estate Down Payment",
                    category="house",
                    target_amount=Decimal("60000.00"),
                    current_amount=Decimal("22000.00"),
                    target_date=date(2029, 12, 31),
                    monthly_contribution=Decimal("1000.00"),
                    expected_annual_return_pct=Decimal("7.0")
                )
            ]
            db.add_all(goals)
            db.commit()
            print(f"Seeded {len(goals)} active savings goals.")

        # 5. Add Debt (Auto Loan)
        d_count = db.query(Debt).filter(Debt.user_id == user.id).count()
        if d_count == 0:
            debts = [
                Debt(
                    user_id=user.id,
                    name="Electric Vehicle Auto Loan",
                    debt_type="auto_loan",
                    principal_amount=Decimal("22000.00"),
                    current_balance=Decimal("14500.00"),
                    interest_rate_apr=Decimal("4.75"),
                    minimum_monthly_payment=Decimal("380.00")
                )
            ]
            db.add_all(debts)
            db.commit()
            print(f"Seeded {len(debts)} debt liability.")

        # 6. Add Portfolio and Holdings
        p_count = db.query(Portfolio).filter(Portfolio.user_id == user.id).count()
        if p_count == 0:
            portfolio = Portfolio(
                user_id=user.id,
                name="Core Strategic Growth Portfolio",
                description="Long-term multi-asset ETF allocation with broad indexing and fixed income buffer."
            )
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)

            holdings = [
                PortfolioHolding(user_id=user.id, portfolio_id=portfolio.id, symbol="VTI", name="Vanguard Total Stock Market Index", asset_class="equity", quantity=Decimal("75.0"), average_buy_price=Decimal("230.00"), current_price=Decimal("275.50")),
                PortfolioHolding(user_id=user.id, portfolio_id=portfolio.id, symbol="VXUS", name="Vanguard Total International Stock", asset_class="equity", quantity=Decimal("80.0"), average_buy_price=Decimal("56.00"), current_price=Decimal("63.20")),
                PortfolioHolding(user_id=user.id, portfolio_id=portfolio.id, symbol="BND", name="Vanguard Total Bond Market ETF", asset_class="fixed_income", quantity=Decimal("90.0"), average_buy_price=Decimal("72.00"), current_price=Decimal("74.80")),
                PortfolioHolding(user_id=user.id, portfolio_id=portfolio.id, symbol="GLD", name="SPDR Gold Shares ETF", asset_class="commodities", quantity=Decimal("15.0"), average_buy_price=Decimal("185.00"), current_price=Decimal("238.40")),
                PortfolioHolding(user_id=user.id, portfolio_id=portfolio.id, symbol="BTC-USD", name="Bitcoin Digital Asset", asset_class="crypto", quantity=Decimal("0.08"), average_buy_price=Decimal("42000.00"), current_price=Decimal("68500.00"))
            ]
            db.add_all(holdings)
            db.commit()
            print(f"Seeded portfolio with {len(holdings)} multi-asset holdings.")

        print("WealthOS AI demo database seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
