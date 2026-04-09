# File: Final_Project_v003/app_fastapi/services/models/random_forest.py
"""Random Forest Classifier Model"""
from typing import Dict
from .base_model import train_model as base_train, predict as base_predict


def train_model(**kwargs) -> Dict:
    """Train Random Forest model"""
    return base_train(model_type="random_forest", **kwargs)


def predict(model_name: str, data: dict) -> Dict:
    """Predict with Random Forest model"""
    return base_predict(model_name, data)