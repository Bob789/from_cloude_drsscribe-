# File: Final_Project_v003/app_fastapi/services/models/knn.py
"""K-Nearest Neighbors Classifier Model"""
from typing import Dict
from .base_model import train_model as base_train, predict as base_predict


def train_model(**kwargs) -> Dict:
    """Train KNN model"""
    return base_train(model_type="knn", **kwargs)


def predict(model_name: str, data: dict) -> Dict:
    """Predict with KNN model"""
    return base_predict(model_name, data)