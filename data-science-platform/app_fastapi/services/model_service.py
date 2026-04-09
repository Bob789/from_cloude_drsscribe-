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