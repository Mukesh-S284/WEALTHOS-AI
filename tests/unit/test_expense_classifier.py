"""Unit tests for Rule Baseline and Hybrid ML Expense Categorizer."""

from ml.expense_classifier.model import RuleBasedCategorizer, ExpenseClassifier


def test_rule_based_categorizer_core_categories():
    engine = RuleBasedCategorizer()

    # Groceries
    cat, conf = engine.predict("WHOLE FOODS SOMA SAN FRANCISCO")
    assert cat == "Groceries"
    assert conf > 0.8

    # Dining
    cat, conf = engine.predict("STARBUCKS COFFEE STORE #0921")
    assert cat == "Dining"
    assert conf > 0.8

    # Utilities
    cat, conf = engine.predict("CON EDISON NY ELECTRIC UTILITY")
    assert cat == "Utilities"

    # Subscriptions
    cat, conf = engine.predict("NETFLIX.COM STREAMING MEMBERSHIP")
    assert cat == "Subscriptions"

    # Transportation
    cat, conf = engine.predict("CHEVRON FUEL GAS STATION")
    assert cat == "Transportation"

    # Income
    cat, conf = engine.predict("ACME CORP PAYROLL DIRECT DEP")
    assert cat == "Income"


def test_hybrid_expense_classifier():
    classifier = ExpenseClassifier()

    # Rule match
    cat, conf, source = classifier.predict("TRADER JOE'S MARKET ARLINGTON")
    assert cat == "Groceries"
    assert source == "rule"
    assert conf >= 0.85

    # Fallback behavior on unclassifiable random text
    unknown_cat, unknown_conf, unknown_source = classifier.predict("XYZ998822KJSHDF")
    assert unknown_cat in ("Miscellaneous", classifier.ml_model.classes_.tolist() if classifier.ml_model else ["Miscellaneous"])
    assert 0.0 <= unknown_conf <= 1.0
