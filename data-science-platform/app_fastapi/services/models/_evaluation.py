# File: Final_Project_v003/app_fastapi/services/models/_evaluation.py
from typing import Dict, Any
import numpy as np

from sklearn.model_selection import (
    train_test_split,
    RepeatedStratifiedKFold,
    RepeatedKFold,
    cross_validate,
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
    log_loss, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score,
)
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.pipeline import Pipeline


def _final_estimator(estimator):
    return estimator.steps[-1][1] if isinstance(estimator, Pipeline) else estimator

def supports_proba(estimator) -> bool:
    return hasattr(_final_estimator(estimator), "predict_proba")


# =========================
# Classification evaluation
# =========================
def evaluate_classification_holdout(
    estimator, X, y, test_size=0.2, random_state=42, stratify=True
) -> Dict[str, Any]:
    stratify_y = y if stratify else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify_y
    )

    estimator.fit(X_train, y_train)

    y_tr_pred = estimator.predict(X_train)
    y_te_pred = estimator.predict(X_test)

    metrics: Dict[str, Any] = {
        "train_accuracy": float(accuracy_score(y_train, y_tr_pred)),
        "test_accuracy": float(accuracy_score(y_test, y_te_pred)),
        "test_precision_weighted": float(precision_score(y_test, y_te_pred, average="weighted", zero_division=0)),
        "test_recall_weighted": float(recall_score(y_test, y_te_pred, average="weighted", zero_division=0)),
        "test_f1_weighted": float(f1_score(y_test, y_te_pred, average="weighted", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_te_pred).tolist(),
        "confusion_matrix_normalized": confusion_matrix(y_test, y_te_pred, normalize="true").tolist(),
    }

    if supports_proba(estimator):
        y_te_proba = estimator.predict_proba(X_test)
        try:
            metrics["test_log_loss"] = float(log_loss(y_test, y_te_proba))
        except Exception:
            pass
        try:
            metrics["test_roc_auc_ovr"] = float(roc_auc_score(y_test, y_te_proba, multi_class="ovr"))
        except Exception:
            pass

    try:
        dummy = DummyClassifier(strategy="most_frequent")
        dummy.fit(X_train, y_train)
        y_dummy = dummy.predict(X_test)
        metrics["baseline_most_frequent_accuracy"] = float(accuracy_score(y_test, y_dummy))
    except Exception:
        pass

    return metrics


def evaluate_classification_cv(
    estimator, X, y, n_splits=5, n_repeats=1, random_state=42
) -> Dict[str, Any]:
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=random_state)

    scorers = {
        "accuracy": "accuracy",
        "precision_weighted": "precision_weighted",
        "recall_weighted": "recall_weighted",
        "f1_weighted": "f1_weighted",
    }
    if supports_proba(estimator):
        scorers["neg_log_loss"] = "neg_log_loss"
        scorers["roc_auc_ovr"] = "roc_auc_ovr"

    cv_results = cross_validate(estimator, X, y, cv=cv, scoring=scorers, n_jobs=-1)

    out: Dict[str, Any] = {}
    for k, v in cv_results.items():
        if k.startswith("test_"):
            name = k.replace("test_", "")
            out[f"{name}_mean"] = float(np.mean(v))
            out[f"{name}_std"] = float(np.std(v))

    try:
        dummy = DummyClassifier(strategy="most_frequent")
        base = cross_validate(dummy, X, y, cv=cv, scoring={"accuracy": "accuracy"}, n_jobs=-1)
        vals = base["test_accuracy"]
        out["baseline_most_frequent_accuracy_mean"] = float(np.mean(vals))
        out["baseline_most_frequent_accuracy_std"] = float(np.std(vals))
    except Exception:
        pass

    return out


# =====================
# Regression evaluation
# =====================
def evaluate_regression_holdout(
    estimator, X, y, test_size=0.2, random_state=42
) -> Dict[str, Any]:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    estimator.fit(X_train, y_train)
    y_tr_pred = estimator.predict(X_train)
    y_te_pred = estimator.predict(X_test)

    mse_train = mean_squared_error(y_train, y_tr_pred)
    mse_test = mean_squared_error(y_test, y_te_pred)

    metrics = {
        "train_r2": float(r2_score(y_train, y_tr_pred)),
        "test_r2": float(r2_score(y_test, y_te_pred)),
        "train_rmse": float(np.sqrt(mse_train)),
        "test_rmse": float(np.sqrt(mse_test)),
        "test_mae": float(mean_absolute_error(y_test, y_te_pred)),
    }

    try:
        dummy = DummyRegressor(strategy="mean")
        dummy.fit(X_train, y_train)
        y_dummy = dummy.predict(X_test)
        metrics["baseline_rmse"] = float(np.sqrt(mean_squared_error(y_test, y_dummy)))
        metrics["baseline_mae"] = float(mean_absolute_error(y_test, y_dummy))
    except Exception:
        pass

    return metrics


def evaluate_regression_cv(
    estimator, X, y, n_splits=5, n_repeats=1, random_state=42
) -> Dict[str, Any]:
    cv = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=random_state)

    scorers = {
        "r2": "r2",
        "neg_root_mean_squared_error": "neg_root_mean_squared_error",
        "neg_mean_absolute_error": "neg_mean_absolute_error",
    }
    cv_results = cross_validate(estimator, X, y, cv=cv, scoring=scorers, n_jobs=-1)

    out: Dict[str, Any] = {}
    for name in ["r2", "neg_root_mean_squared_error", "neg_mean_absolute_error"]:
        vals = cv_results[f"test_{name}"]
        out[f"{name}_mean"] = float(np.mean(vals))
        out[f"{name}_std"] = float(np.std(vals))

    # Convert negatives to positives
    out["rmse_mean"] = float(-out.pop("neg_root_mean_squared_error_mean"))
    out["rmse_std"] = float(out.pop("neg_root_mean_squared_error_std"))  # STD is always positive, no negation needed
    out["mae_mean"] = float(-out.pop("neg_mean_absolute_error_mean"))
    out["mae_std"] = float(out.pop("neg_mean_absolute_error_std"))  # STD is always positive, no negation needed

    try:
        dummy = DummyRegressor(strategy="mean")
        base = cross_validate(dummy, X, y, cv=cv, scoring={"neg_root_mean_squared_error": "neg_root_mean_squared_error"}, n_jobs=-1)
        rmse_vals = -base["test_neg_root_mean_squared_error"]
        out["baseline_rmse_mean"] = float(np.mean(rmse_vals))
        out["baseline_rmse_std"] = float(np.std(rmse_vals))
    except Exception:
        pass

    return out