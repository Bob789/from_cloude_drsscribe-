# File: Final_Project_v003/app_fastapi/services/models/linear_regression.py
"""Linear Regression Model"""
from typing import Dict
from .base_model import train_model as base_train, predict as base_predict


def train_model(**kwargs) -> Dict:
    """Train Linear Regression model"""
    return base_train(model_type="linear_regression", **kwargs)


def predict(model_name: str, data: dict) -> Dict:
    """Predict with Linear Regression model"""
    return base_predict(model_name, data)