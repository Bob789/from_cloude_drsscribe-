# File: Final_Project_v003/app_fastapi/services/models/svm.py
"""Support Vector Machine (Linear) Classifier Model"""
from typing import Dict
from .base_model import train_model as base_train, predict as base_predict


def train_model(**kwargs) -> Dict:
    """Train SVM model"""
    return base_train(model_type="svm", **kwargs)


def predict(model_name: str, data: dict) -> Dict:
    """Predict with SVM model"""
    return base_predict(model_name, data)