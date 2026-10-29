"""Unit tests for Financial Health Reporting service."""

from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session

from backend.services.report_service import HealthReportService
from backend.models.user import User
from backend.models.transaction import Transaction
from backend.models.debt import Debt
from backend.models.savings import SavingsGoal


def test_health_report_baseline_empty_user(db_session: Session, test_user: User):
    service = HealthReportService(db_session)
    report = service.generate_health_report(test_user)

    assert 0 <= report.overall_health_score <= 100
    assert report.rating in ("Excellent", "Good", "Fair", "Needs Attention")
    assert len(report.indicators) == 7
    # Verify indicators sum matches overall score
    assert sum(ind.score for ind in report.indicators) == report.overall_health_score
    assert report.disclaimer


def test_health_report_high_performing_user(db_session: Session, test_user: User):
    # Add healthy income and modest expense
    tx_inc = Transaction(
        user_id=test_user.id,
        date=date.today(),
        amount=Decimal("8000.00"),
        type="income",
        category="Salary",
        description="Monthly Salary"
    )
    tx_exp = Transaction(
        user_id=test_user.id,
        date=date.today(),
        amount=Decimal("3000.00"),
        type="expense",
        category="Rent",
        description="Housing"
    )
    # Add modest debt
    debt = Debt(
        user_id=test_user.id,
        name="Auto Loan",
        debt_type="auto_loan",
        principal_amount=Decimal("5000.00"),
        current_balance=Decimal("5000.00"),
        interest_rate_apr=Decimal("4.5"),
        minimum_monthly_payment=Decimal("200.00")
    )
    # Add savings goal
    goal = SavingsGoal(
        user_id=test_user.id,
        title="Emergency Cushion",
        target_amount=Decimal("15000.00"),
        current_amount=Decimal("12000.00"),
        target_date=date(2027, 12, 31),
        monthly_contribution=Decimal("500.00")
    )
    db_session.add_all([tx_inc, tx_exp, debt, goal])
    db_session.commit()

    service = HealthReportService(db_session)
    report = service.generate_health_report(test_user)

    assert report.monthly_income == Decimal("8000.00")
    assert report.total_expenses == Decimal("3000.00")
    assert report.net_savings == Decimal("5000.00")
    assert report.savings_rate_pct == 62.5
    assert report.overall_health_score >= 70
    assert report.rating in ("Good", "Excellent")
    assert len(report.strengths) > 0
