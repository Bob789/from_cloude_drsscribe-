# File: Final_Project_v003/app_fastapi/core/preprocessing.py
"""
Preprocessing - Creates a complete Pipeline to prevent data leakage
Serves all models
"""
from typing import List
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

def create_preprocessor(
    df: pd.DataFrame,
    feature_columns: List[str],
    scale_features: bool = True
) -> ColumnTransformer:
    """
    Creates preprocessor that handles:
    - Numeric: imputation + scaling (optional)
    - Categorical: imputation + one-hot encoding

    Args:
        df: Original DataFrame
        feature_columns: List of features
        scale_features: Whether to perform scaling (True for most models)
    """
    from .data_handler import get_column_types

    numeric_cols, categorical_cols = get_column_types(df, feature_columns)

    transformers = []

    # Numeric pipeline
    if numeric_cols:
        num_steps = [("imputer", SimpleImputer(strategy="mean"))]
        if scale_features:
            num_steps.append(("scaler", StandardScaler()))
        transformers.append(("num", Pipeline(steps=num_steps), numeric_cols))

    # Categorical pipeline
    if categorical_cols:
        cat_steps = [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ]
        transformers.append(("cat", Pipeline(steps=cat_steps), categorical_cols))

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop"
    )

    return preprocessor

def get_preprocessing_metadata(
    df: pd.DataFrame,
    feature_columns: List[str],
    scale_features: bool = True
) -> dict:
    """
    Returns information about the preprocessing that was performed
    """
    from .data_handler import get_column_types

    numeric_cols, categorical_cols = get_column_types(df, feature_columns)

    transformers_info = {
        "numeric": ["SimpleImputer(mean)"],
        "categorical": ["SimpleImputer(most_frequent)", "OneHotEncoder(handle_unknown='ignore')"]
    }

    if scale_features:
        transformers_info["numeric"].append("StandardScaler()")

    return {
        "strategy": "sklearn-pipeline",
        "note": "All preprocessing inside Pipeline - no data leakage",
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "scale_features": scale_features,
        "transformers": transformers_info
    }