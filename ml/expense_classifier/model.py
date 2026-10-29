"""Expense Categorization Engine: Transparent Rule Baseline and ML Model."""

import re
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import joblib


RULE_PATTERNS = {
    "Groceries": [
        r"whole\s*foods", r"trader\s*joe", r"safeway", r"kroger", r"wal-?mart.*grocery",
        r"aldi", r"costco", r"sprouts", r"heb", r"market", r"grocery", r"supermarket"
    ],
    "Dining": [
        r"starbucks", r"chipotle", r"mcdonald", r"panera", r"sweetgreen", r"burger",
        r"uber\s*eats", r"doordash", r"shake\s*shack", r"coffee", r"cafe", r"pizza",
        r"subway", r"restaurant", r"bistro", r"taco", r"sushi", r"bakery", r"diner"
    ],
    "Housing": [
        r"rent", r"mortgage", r"property\s*mgmt", r"hoa", r"landlord", r"apartment",
        r"residential", r"realty", r"lease"
    ],
    "Utilities": [
        r"electric", r"gas\s*&?\s*electric", r"water", r"sewer", r"trash", r"waste",
        r"at&t", r"verizon", r"t-mobile", r"comcast", r"xfinity", r"spectrum", r"utility"
    ],
    "Transportation": [
        r"shell", r"chevron", r"exxon", r"fuel", r"gas\s*station", r"uber(\s*trip|\*ride)?",
        r"lyft", r"mta\s*subway", r"bart", r"transit", r"airline", r"flight", r"delta",
        r"united", r"american\s*air", r"toll", r"parking", r"car\s*rental"
    ],
    "Subscriptions": [
        r"netflix", r"spotify", r"icloud", r"apple\.com/bill", r"youtube\s*premium",
        r"prime\s*video", r"hbo", r"disney\s*plus", r"nyt", r"subscription", r"openai",
        r"chatgpt", r"github"
    ],
    "Shopping": [
        r"amazon", r"best\s*buy", r"apple\s*store", r"zara", r"h&m", r"nike",
        r"ikea", r"home\s*depot", r"sephora", r"clothing", r"apparel", r"store"
    ],
    "Healthcare": [
        r"cvs", r"walgreens", r"pharmacy", r"kaiser", r"clinic", r"doctor", r"hospital",
        r"dental", r"dentist", r"vision", r"lab\s*work", r"urgent\s*care", r"medical"
    ],
    "Income": [
        r"payroll", r"salary", r"direct\s*dep", r"wage", r"stipend", r"tax\s*refund",
        r"stripe\s*payout", r"bonus", r"disbursement", r"freelance"
    ],
    "Investments": [
        r"vanguard", r"fidelity", r"schwab", r"robinhood", r"coinbase", r"brokerage",
        r"index\s*fund", r"stock", r"crypto", r"etf"
    ]
}


class RuleBasedCategorizer:
    """Deterministic, transparent keyword matching baseline."""

    def __init__(self):
        self.rules = {
            cat: [re.compile(p, re.IGNORECASE) for p in patterns]
            for cat, patterns in RULE_PATTERNS.items()
        }

    def predict(self, text: str) -> Tuple[Optional[str], float]:
        """Classify transaction description. Returns (category, confidence)."""
        clean_text = text.strip().lower()
        for cat, patterns in self.rules.items():
            for pat in patterns:
                if pat.search(clean_text):
                    return cat, 0.90 # Strong heuristic confidence
        return None, 0.0


class ExpenseClassifier:
    """Production categorizer combining Rule Baseline and Trained ML Model."""

    def __init__(self, model_path: Optional[str] = None):
        self.rule_engine = RuleBasedCategorizer()
        self.ml_model = None
        self.model_path = model_path or str(
            Path(__file__).resolve().parent.parent / "artifacts" / "expense_classifier.joblib"
        )
        self.load_model()

    def load_model(self) -> bool:
        """Attempt loading trained scikit-learn model artifact."""
        try:
            path = Path(self.model_path)
            if path.exists():
                self.ml_model = joblib.load(path)
                return True
        except Exception:
            self.ml_model = None
        return False

    def predict(self, description: str) -> Tuple[str, float, str]:
        """
        Classify transaction description into category with confidence and source tag.
        Returns: (category, confidence, source)
        Source is one of: 'rule', 'ml', or 'default'
        """
        # 1. Rule-based baseline evaluation
        rule_cat, rule_conf = self.rule_engine.predict(description)
        if rule_cat:
            return rule_cat, rule_conf, "rule"

        # 2. Machine Learning model evaluation
        if self.ml_model is not None:
            try:
                # Expecting pipeline with predict_proba
                probs = self.ml_model.predict_proba([description])[0]
                classes = self.ml_model.classes_
                max_idx = probs.argmax()
                ml_cat = classes[max_idx]
                ml_conf = float(probs[max_idx])
                
                if ml_conf >= 0.35:
                    return ml_cat, ml_conf, "ml"
            except Exception:
                pass

        # 3. Default fallback
        return "Miscellaneous", 0.20, "default"
