"""Training and evaluation pipeline for expense categorization."""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from typing import Dict, Any
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix
import joblib

from ml.expense_classifier.dataset import get_labeled_data
from ml.expense_classifier.model import RuleBasedCategorizer


def train_and_evaluate(random_state: int = 42) -> Dict[str, Any]:
    """Train TF-IDF + Logistic Regression model and evaluate against Rule baseline."""
    texts, labels = get_labeled_data()
    
    # Stratified split to prevent leakage
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=random_state, stratify=labels
    )
    
    # 1. Evaluate Rule-based baseline on test set
    rule_engine = RuleBasedCategorizer()
    rule_preds = []
    for text in X_test:
        cat, _ = rule_engine.predict(text)
        rule_preds.append(cat or "Miscellaneous")
    
    rule_acc = accuracy_score(y_test, rule_preds)
    rule_f1 = f1_score(y_test, rule_preds, average="weighted", zero_division=0)

    # 2. Train ML Pipeline: TF-IDF + Logistic Regression
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, lowercase=True)),
        ("clf", LogisticRegression(C=1.5, max_iter=1000, random_state=random_state))
    ])
    
    pipeline.fit(X_train, y_train)
    ml_preds = pipeline.predict(X_test)
    
    ml_acc = accuracy_score(y_test, ml_preds)
    ml_f1 = f1_score(y_test, ml_preds, average="weighted", zero_division=0)
    report_dict = classification_report(y_test, ml_preds, output_dict=True, zero_division=0)
    conf_matrix = confusion_matrix(y_test, ml_preds, labels=pipeline.classes_).tolist()

    # Save model artifact
    artifact_dir = Path(__file__).resolve().parent.parent / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "expense_classifier.joblib"
    joblib.dump(pipeline, artifact_path)

    results = {
        "dataset_size": len(texts),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "rule_baseline": {
            "accuracy": float(rule_acc),
            "f1_score": float(rule_f1)
        },
        "ml_model": {
            "accuracy": float(ml_acc),
            "f1_score": float(ml_f1),
            "classification_report": report_dict,
            "classes": pipeline.classes_.tolist(),
            "confusion_matrix": conf_matrix
        },
        "artifact_path": str(artifact_path)
    }

    return results


if __name__ == "__main__":
    res = train_and_evaluate()
    print("=== Training & Evaluation Complete ===")
    print(f"Dataset: {res['dataset_size']} items (Train: {res['train_size']}, Test: {res['test_size']})")
    print(f"Rule Baseline Accuracy: {res['rule_baseline']['accuracy']:.4f}, F1: {res['rule_baseline']['f1_score']:.4f}")
    print(f"ML Model Accuracy:      {res['ml_model']['accuracy']:.4f}, F1: {res['ml_model']['f1_score']:.4f}")
    print(f"Saved artifact to: {res['artifact_path']}")
