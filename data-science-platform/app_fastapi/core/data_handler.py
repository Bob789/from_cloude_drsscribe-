# File: Final_Project_v003/app_fastapi/core/data_handler.py
"""
Data Handler - Handles CSV loading and basic validation
"""
import pandas as pd
from typing import List, Tuple

def load_and_validate_csv(
    file_path: str,
    feature_columns: List[str],
    label_column: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """
    Loads CSV and validates that the columns exist

    Returns:
        df: Full DataFrame
        X: Features
        y: Labels
    """
    df = pd.read_csv(file_path)

    # Validation
    missing_cols = set(feature_columns + [label_column]) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    X = df[feature_columns].copy()
    y = df[label_column].copy()

    return df, X, y

def get_column_types(df: pd.DataFrame, feature_columns: List[str]) -> Tuple[List[str], List[str]]:
    """
    Divides columns into numeric and categorical
    """
    X = df[feature_columns]
    numeric_cols = [c for c in feature_columns if pd.api.types.is_numeric_dtype(X[c])]
    categorical_cols = [c for c in feature_columns if not pd.api.types.is_numeric_dtype(X[c])]

    return numeric_cols, categorical_cols
