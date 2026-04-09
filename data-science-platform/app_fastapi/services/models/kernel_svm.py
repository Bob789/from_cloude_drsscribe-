# File: Final_Project_v003/app_fastapi/services/models/kernel_svm.py
"""Kernel SVM (RBF) Classifier Model"""
from typing import Dict
from .base_model import train_model as base_train, predict as base_predict


def train_model(**kwargs) -> Dict:
    """Train Kernel SVM model"""
    return base_train(model_type="kernel_svm", **kwargs)


def predict(model_name: str, data: dict) -> Dict:
    """Predict with Kernel SVM model"""
    return base_predict(model_name, data)