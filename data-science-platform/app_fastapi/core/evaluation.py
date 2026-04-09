# File: app_fastapi/core/evaluation.py
"""
Evaluation module for model metrics and performance assessment.

Supports classification and regression models with holdout and cross-validation.
"""

from typing import Dict, Any
import numpy as np
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold, RepeatedKFold, cross_validate
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
                             log_loss, roc_auc_score, mean_squared_error, mean_absolute_error, r2_score)
from sklearn.dummy import DummyClassifier, DummyRegressor


def supports_proba(estimator) -> bool:
    """Check if the model supports probability predictions."""
    from sklearn.pipeline import Pipeline
    final = estimator.steps[-1][1] if isinstance(estimator, Pipeline) else estimator
    return hasattr(final, "predict_proba")


def evaluate_classification_holdout(estimator, X, y, test_size=0.2, random_state=42, stratify=True) -> Dict[str, Any]:
    """Evaluate classification model with train/test split."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y if stratify else None)
    estimator.fit(X_train, y_train)

    y_train_pred, y_test_pred = estimator.predict(X_train), estimator.predict(X_test)
    metrics = {
        "train_accuracy": float(accuracy_score(y_train, y_train_pred)),
        "test_accuracy": float(accuracy_score(y_test, y_test_pred)),
        "test_precision": float(precision_score(y_test, y_test_pred, average="weighted", zero_division=0)),
        "test_recall": float(recall_score(y_test, y_test_pred, average="weighted", zero_division=0)),
        "test_f1": float(f1_score(y_test, y_test_pred, average="weighted", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_test_pred).tolist()
    }

    if supports_proba(estimator):
        try:
            proba = estimator.predict_proba(X_test)
            metrics["test_log_loss"] = float(log_loss(y_test, proba))
            metrics["test_roc_auc"] = float(roc_auc_score(y_test, proba, multi_class="ovr", average="weighted"))
        except Exception:
            pass

    try:
        dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
        metrics["baseline_accuracy"] = float(accuracy_score(y_test, dummy.predict(X_test)))
    except Exception:
        pass
    return metrics


def evaluate_classification_cv(estimator, X, y, n_splits=5, n_repeats=1, random_state=42) -> Dict[str, Any]:
    """Evaluate classification model with cross-validation."""
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=random_state)
    scorers = {"accuracy": "accuracy", "precision": "precision_weighted",
               "recall": "recall_weighted", "f1": "f1_weighted"}
    if supports_proba(estimator):
        scorers.update({"neg_log_loss": "neg_log_loss", "roc_auc": "roc_auc_ovr_weighted"})

    cv_results = cross_validate(estimator, X, y, cv=cv, scoring=scorers, n_jobs=-1, return_train_score=False)
    metrics = _process_cv_results(cv_results)

    try:
        dummy = DummyClassifier(strategy="most_frequent")
        base = cross_validate(dummy, X, y, cv=cv, scoring={"accuracy": "accuracy"}, n_jobs=-1)
        metrics["baseline_accuracy_mean"] = float(np.mean(base["test_accuracy"]))
    except Exception:
        pass
    return metrics


def evaluate_regression_holdout(estimator, X, y, test_size=0.2, random_state=42) -> Dict[str, Any]:
    """Evaluate regression model with train/test split."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    estimator.fit(X_train, y_train)

    y_train_pred, y_test_pred = estimator.predict(X_train), estimator.predict(X_test)
    metrics = {
        "train_r2": float(r2_score(y_train, y_train_pred)),
        "train_rmse": float(np.sqrt(mean_squared_error(y_train, y_train_pred))),
        "test_r2": float(r2_score(y_test, y_test_pred)),
        "test_rmse": float(np.sqrt(mean_squared_error(y_test, y_test_pred))),
        "test_mae": float(mean_absolute_error(y_test, y_test_pred))
    }

    try:
        dummy = DummyRegressor(strategy="mean").fit(X_train, y_train)
        metrics["baseline_rmse"] = float(np.sqrt(mean_squared_error(y_test, dummy.predict(X_test))))
    except Exception:
        pass
    return metrics


def evaluate_regression_cv(estimator, X, y, n_splits=5, n_repeats=1, random_state=42) -> Dict[str, Any]:
    """Evaluate regression model with cross-validation."""
    cv = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=random_state)
    scorers = {"r2": "r2", "rmse": "neg_root_mean_squared_error", "mae": "neg_mean_absolute_error"}
    cv_results = cross_validate(estimator, X, y, cv=cv, scoring=scorers, n_jobs=-1, return_train_score=False)
    metrics = _process_cv_results(cv_results, negative_metrics={"rmse", "mae"})

    try:
        dummy = DummyRegressor(strategy="mean")
        base = cross_validate(dummy, X, y, cv=cv, scoring={"rmse": "neg_root_mean_squared_error"}, n_jobs=-1)
        metrics["baseline_rmse_mean"] = float(-np.mean(base["test_rmse"]))
    except Exception:
        pass
    return metrics


def _process_cv_results(cv_results: dict, negative_metrics: set = None) -> Dict[str, Any]:
    """Process cross-validation results into mean and std metrics."""
    negative_metrics = negative_metrics or set()
    metrics = {}
    for key, values in cv_results.items():
        if key.startswith("test_"):
            is_neg = "neg_" in key
            name = key.replace("test_", "").replace("neg_", "")
            mean_val = float(np.mean(values))
            if is_neg or name in negative_metrics:
                mean_val = -mean_val
            metrics[f"{name}_mean"] = mean_val
            metrics[f"{name}_std"] = float(np.std(values))
    return metrics


def format_metrics_summary(metrics: Dict[str, Any], model_type: str, eval_strategy: str) -> str:
    """Create a readable summary of metrics for display."""
    if not metrics:
        return "No metrics available"

    is_class = model_type in ["logistic_regression", "decision_tree", "random_forest", "knn", "svm", "kernel_svm"]
    if is_class:
        acc = metrics.get("accuracy_mean" if eval_strategy == "cv" else "test_accuracy", 0)
        f1 = metrics.get("f1_mean" if eval_strategy == "cv" else "test_f1", 0)
        return f"Accuracy: {acc:.2%} | F1: {f1:.4f}"
    else:
        r2 = metrics.get("r2_mean" if eval_strategy == "cv" else "test_r2", 0)
        rmse = metrics.get("rmse_mean" if eval_strategy == "cv" else "test_rmse", 0)
        return f"R2: {r2:.4f} | RMSE: {rmse:.4f}"
