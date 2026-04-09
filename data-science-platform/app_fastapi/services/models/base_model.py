# File: Final_Project_v003/app_fastapi/services/models/base_model.py
"""
Base Model - One template for all models!
This file does all the heavy lifting.
"""
import pandas as pd
from typing import Dict, List, Optional
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from app_fastapi.core.data_handler import load_and_validate_csv
from app_fastapi.core.preprocessing import create_preprocessor, get_preprocessing_metadata
from app_fastapi.core.evaluation import (
    evaluate_classification_holdout,
    evaluate_classification_cv,
    evaluate_regression_holdout,
    evaluate_regression_cv,
    format_metrics_summary
)
from app_fastapi.core.model_manager import save_model, load_model, load_metadata
from .config import get_model_config


def train_model(
        file_path: str,
        model_name: str,
        model_type: str,
        feature_columns: List[str],
        label_column: str,
        test_size: float = 0.2,
        random_state: int = 42,
        evaluation_strategy: str = "cv",
        cv_folds: int = 5,
        cv_repeats: int = 1,
        stratify: bool = True,
        primary_metric: Optional[str] = None,
        **kwargs
) -> Dict:
    """
    Single function that trains any type of model!
    """
    # 1. Get model configuration
    config = get_model_config(model_type)

    # 2. Load data
    df, X, y = load_and_validate_csv(file_path, feature_columns, label_column)

    # 3. Handle Label Encoding (if required)
    label_encoder = None
    classes = None

    if config.get("needs_label_encoding", False):
        label_encoder = LabelEncoder()
        y = pd.Series(label_encoder.fit_transform(y.astype(str)))
        classes = label_encoder.classes_.tolist()
    else:
        # Regression - convert to numbers
        y = pd.to_numeric(y, errors="coerce").fillna(y.mean())

    # 4. Create Pipeline
    preprocessor = create_preprocessor(df, feature_columns, scale_features=config["needs_scaling"])

    # 5. Create Estimator with parameters
    estimator_params = {**config["default_params"], **kwargs}

    # Add random_state only if the model supports it
    if config.get("supports_random_state", True):
        estimator_params["random_state"] = random_state

    estimator_class = config["estimator_class"]
    estimator = estimator_class(**estimator_params)

    # 6. Build full Pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("estimator", estimator)
    ])

    # 7. Evaluate model
    is_classification = config["type"] == "classification"

    if evaluation_strategy == "holdout":
        if is_classification:
            metrics = evaluate_classification_holdout(pipeline, X, y, test_size, random_state, stratify)
        else:
            metrics = evaluate_regression_holdout(pipeline, X, y, test_size, random_state)
    else:  # cv
        if is_classification:
            metrics = evaluate_classification_cv(pipeline, X, y, cv_folds, cv_repeats, random_state)
        else:
            metrics = evaluate_regression_cv(pipeline, X, y, cv_folds, cv_repeats, random_state)

        # Add aliases for metrics (without _mean) for compatibility
        if is_classification:
            for key in ["accuracy", "precision", "recall", "f1", "log_loss", "roc_auc"]:
                if f"{key}_mean" in metrics:
                    metrics[key] = metrics[f"{key}_mean"]
        else:
            for key in ["r2", "rmse", "mae"]:
                if f"{key}_mean" in metrics:
                    metrics[key] = metrics[f"{key}_mean"]
            # Add mse if rmse exists
            if "rmse" in metrics:
                metrics["mse"] = metrics["rmse"] ** 2

        # Fit on all data after CV
        pipeline.fit(X, y)

        # Add confusion_matrix for classification models (on all data)
        if is_classification:
            from sklearn.metrics import confusion_matrix
            y_pred_full = pipeline.predict(X)
            metrics["confusion_matrix"] = confusion_matrix(y, y_pred_full).tolist()

    # 8. Create metadata
    metadata = {
        "model_name": model_name,
        "model_type": model_type,
        "feature_columns": feature_columns,
        "label_column": label_column,
        "preprocessing": get_preprocessing_metadata(df, feature_columns, config["needs_scaling"]),
        "evaluation": {
            "strategy": evaluation_strategy,
            "cv_folds": cv_folds if evaluation_strategy == "cv" else None,
            "cv_repeats": cv_repeats if evaluation_strategy == "cv" else None,
            "test_size": test_size if evaluation_strategy == "holdout" else None,
            "stratify": stratify if is_classification else None,
            "primary_metric": primary_metric
        },
        "hyperparameters": estimator_params,
        "metrics": metrics,
        "classes": classes,
        "label_encoder_used": label_encoder is not None,
        "metrics_summary": format_metrics_summary(metrics, model_type, evaluation_strategy)
    }

    # 9. Save model
    save_model(model_name, pipeline, metadata)

    return metadata


def predict(model_name: str, data: dict) -> Dict:
    """
    Single prediction function for all models.
    """
    # Load model and metadata
    pipeline = load_model(model_name)
    metadata = load_metadata(model_name)

    feature_columns = metadata["feature_columns"]
    model_type = metadata["model_type"]
    classes = metadata.get("classes")

    # Prepare data
    X_new = pd.DataFrame([[data.get(col, None) for col in feature_columns]], columns=feature_columns)

    # Predict
    prediction = pipeline.predict(X_new)[0]

    # Return prediction
    if classes:
        predicted_class = classes[prediction]
        # If the class is a string representing a number, convert to integer
        try:
            predicted_value = int(predicted_class)
        except (ValueError, TypeError):
            predicted_value = predicted_class
    else:
        predicted_value = float(prediction)

    result = {
        "model_name": model_name,
        "model_type": model_type,
        "prediction": predicted_value
    }

    # Probabilities (if available)
    config = get_model_config(model_type)
    if config["supports_proba"]:
        proba = pipeline.predict_proba(X_new)[0]
        result["prediction_probabilities"] = proba.tolist()

    return result
