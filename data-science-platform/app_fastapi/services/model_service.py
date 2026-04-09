# File: Final_Project_v003/app_fastapi/services/model_service.py
import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

MODELS_DIR = "app_fastapi/models/trained"
METADATA_DIR = "app_fastapi/models/metadata"
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

from .models import MODEL_REGISTRY
from .models.config import MODEL_CONFIG, get_model_config


def preprocess_dataframe(df: pd.DataFrame, feature_columns: List[str], label_column: str) -> tuple:
    # NOTE: Kept for internal/backward use, but in practice preprocessing is done inside Pipeline
    df_processed = df.copy()
    preprocessing_info = {
        "one_hot_columns": [],
        "date_columns": [],
        "numeric_columns": [],
        "dropped_columns": []
    }

    X = df_processed[feature_columns].copy()
    y = df_processed[label_column].copy()

    for col in feature_columns:
        if X[col].dtype == 'object':
            one_hot = pd.get_dummies(X[col], prefix=col, drop_first=True)
            X = pd.concat([X, one_hot], axis=1)
            X = X.drop(columns=[col])
            preprocessing_info["one_hot_columns"].append(col)
        else:
            if X[col].isna().any():
                mean_val = X[col].mean()
                X[col] = X[col].fillna(mean_val)
            preprocessing_info["numeric_columns"].append(col)

    y = pd.to_numeric(y, errors='coerce')
    y = y.fillna(y.mean())

    return X, y, preprocessing_info


def train_model_from_csv(
        file_path: str,
        model_name: str,
        feature_columns: List[str],
        label_column: str,
        test_size: float = 0.2,
        random_state: int = 42,
        model_type: str = "linear_regression",
        evaluation_strategy: str = "cv",
        cv_folds: int = 5,
        cv_repeats: int = 1,
        stratify: bool = True,
        primary_metric: Optional[str] = None,
        **kwargs
) -> Dict:
    if model_type not in MODEL_REGISTRY:
        supported = ", ".join(MODEL_REGISTRY.keys())
        raise ValueError(f"Unsupported model type '{model_type}'. Supported: {supported}")

    model_module = MODEL_REGISTRY[model_type]

    return model_module.train_model(
        file_path=file_path,
        model_name=model_name,
        feature_columns=feature_columns,
        label_column=label_column,
        test_size=test_size,
        random_state=random_state,
        evaluation_strategy=evaluation_strategy,
        cv_folds=cv_folds,
        cv_repeats=cv_repeats,
        stratify=stratify,
        primary_metric=primary_metric,
        **kwargs
    )


def predict_with_model(model_name: str, data: dict) -> Dict:
    model_path = os.path.join(MODELS_DIR, f"{model_name}.pkl")
    metadata_path = os.path.join(METADATA_DIR, f"{model_name}.json")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model '{model_name}' not found")

    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        model_type = metadata.get("model_type", "linear_regression")
    else:
        model_type = "linear_regression"

    if model_type not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model type '{model_type}' in metadata")

    model_module = MODEL_REGISTRY[model_type]

    return model_module.predict(model_name=model_name, data=data)


def list_all_models() -> List[Dict]:
    models = []
    files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".pkl")]

    for file in files:
        model_name = file.replace(".pkl", "")
        metadata_path = os.path.join(METADATA_DIR, f"{model_name}.json")

        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {"model_name": model_name}

        models.append(metadata)

    return models


def get_model_details(model_name: str) -> Dict:
    model_path = os.path.join(MODELS_DIR, f"{model_name}.pkl")
    metadata_path = os.path.join(METADATA_DIR, f"{model_name}.json")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model '{model_name}' not found")

    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {"model_name": model_name, "metadata": "Not available"}

    return metadata


def delete_model(model_name: str) -> Dict:
    model_path = os.path.join(MODELS_DIR, f"{model_name}.pkl")
    metadata_path = os.path.join(METADATA_DIR, f"{model_name}.json")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model '{model_name}' not found")

    os.remove(model_path)

    if os.path.exists(metadata_path):
        os.remove(metadata_path)

    return {"message": f"Model '{model_name}' deleted successfully"}


def compare_models(
        file_path: str,
        feature_columns: List[str],
        label_column: str,
        test_size: float = 0.2,
        random_state: int = 42,
        evaluation_strategy: str = "cv",
        cv_folds: int = 5,
        task_type: str = "auto",
) -> Dict:
    """Compare all applicable models on the same dataset without saving."""
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import LabelEncoder
    from app_fastapi.core.data_handler import load_and_validate_csv
    from app_fastapi.core.preprocessing import create_preprocessor
    from app_fastapi.core.evaluation import (
        evaluate_classification_holdout, evaluate_classification_cv,
        evaluate_regression_holdout, evaluate_regression_cv,
        format_metrics_summary,
    )

    df, X, y = load_and_validate_csv(file_path, feature_columns, label_column)

    # Auto-detect task type
    if task_type == "auto":
        nunique = y.nunique()
        is_numeric = pd.api.types.is_numeric_dtype(y)
        task_type = "regression" if is_numeric and nunique > 15 else "classification"

    # Filter models by task type
    applicable = {k: v for k, v in MODEL_CONFIG.items() if v["type"] == task_type}

    results = []
    for model_type, config in applicable.items():
        try:
            # Prepare y per model
            if config.get("needs_label_encoding", False):
                le = LabelEncoder()
                y_enc = pd.Series(le.fit_transform(y.astype(str)))
            else:
                y_enc = pd.to_numeric(y, errors="coerce").fillna(y.mean())

            preprocessor = create_preprocessor(df, feature_columns, scale_features=config["needs_scaling"])
            params = dict(config["default_params"])
            if config.get("supports_random_state", True):
                params["random_state"] = random_state
            estimator = config["estimator_class"](**params)
            pipeline = Pipeline([("preprocessor", preprocessor), ("estimator", estimator)])

            is_cls = task_type == "classification"
            if evaluation_strategy == "holdout":
                metrics = (evaluate_classification_holdout(pipeline, X, y_enc, test_size, random_state)
                           if is_cls else evaluate_regression_holdout(pipeline, X, y_enc, test_size, random_state))
            else:
                metrics = (evaluate_classification_cv(pipeline, X, y_enc, cv_folds, 1, random_state)
                           if is_cls else evaluate_regression_cv(pipeline, X, y_enc, cv_folds, 1, random_state))

            # Add compatibility aliases for CV
            if evaluation_strategy == "cv":
                if is_cls:
                    for k in ["accuracy", "precision", "recall", "f1"]:
                        if f"{k}_mean" in metrics:
                            metrics[k] = metrics[f"{k}_mean"]
                else:
                    for k in ["r2", "rmse", "mae"]:
                        if f"{k}_mean" in metrics:
                            metrics[k] = metrics[f"{k}_mean"]

            summary = format_metrics_summary(metrics, model_type, evaluation_strategy)
            results.append({
                "model_type": model_type,
                "metrics": metrics,
                "summary": summary,
                "status": "success",
            })
        except Exception as e:
            results.append({
                "model_type": model_type,
                "metrics": {},
                "summary": str(e),
                "status": "error",
            })

    # Sort: classification by accuracy desc, regression by r2 desc
    if task_type == "classification":
        results.sort(key=lambda r: r["metrics"].get("accuracy", r["metrics"].get("accuracy_mean", 0)), reverse=True)
        best_metric = "accuracy"
    else:
        results.sort(key=lambda r: r["metrics"].get("r2", r["metrics"].get("r2_mean", 0)), reverse=True)
        best_metric = "r2"

    best = results[0]["model_type"] if results and results[0]["status"] == "success" else None

    return {
        "task_type": task_type,
        "models_compared": len(results),
        "best_model": best,
        "best_metric": best_metric,
        "evaluation_strategy": evaluation_strategy,
        "results": results,
    }