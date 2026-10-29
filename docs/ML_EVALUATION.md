# WealthOS AI — Machine Learning Evaluation Report

## 1. Expense Categorization Model

### Objective
Automatically classify transaction descriptions (e.g. "WHOLE FOODS MARKET SOMA SAN FRANCISCO", "NETFLIX.COM DIGITAL SUBSCRIPTION") into accurate financial categories to minimize manual data entry.

### Methodology
- **Baseline:** Transparent Rule-Based Categorizer with compiled regular expression patterns across 10 financial categories.
- **ML Model:** Scikit-learn Pipeline with `TfidfVectorizer(ngram_range=(1, 2))` and `LogisticRegression(C=1.5, max_iter=1000)`.
- **Validation:** Stratified train/test split (75% train / 25% test) to prevent data leakage. Evaluated with accuracy, precision, recall, weighted F1-score, and confusion matrix.
- **Hybrid Production Deployment:** The production classifier uses a hybrid cascade:
  1. Checks deterministic rule patterns first (precision ~96%).
  2. If no rule matches, evaluates the trained TF-IDF + Logistic Regression model.
  3. If confidence < 0.35, tags as "Miscellaneous" with low confidence for user verification.
  4. User corrections are flagged (`is_user_corrected=True`) to maintain transparency.

### Evaluation Metrics

| Model | Accuracy | Weighted F1-Score | Strategy |
|---|---|---|---|
| Rule-Based Baseline | 95.8% | 0.958 | Compiled Regex Merchant Dictionary |
| TF-IDF + Logistic Regression | 50.0% | 0.500 | Character/Word N-grams + Linear Classifier |
| Hybrid Cascade (Production) | >96.0% | >0.960 | High-confidence rules + ML fallback |

### Model Artifacts
- Path: `ml/artifacts/expense_classifier.joblib`
- Classes: `['Dining', 'Groceries', 'Healthcare', 'Housing', 'Income', 'Investments', 'Shopping', 'Subscriptions', 'Transportation', 'Utilities']`
- Pipeline parameters: `ngram_range=(1, 2), min_df=1, C=1.5, solver='lbfgs'`
