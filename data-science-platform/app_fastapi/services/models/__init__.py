# File: Final_Project_v003/app_fastapi/services/models/__init__.py
"""
Model Registry - Registration of all models
"""
from . import (
    linear_regression,
    logistic_regression,
    decision_tree,
    random_forest,
    knn,
    svm,
    kernel_svm
)

MODEL_REGISTRY = {
    "linear_regression": linear_regression,
    "logistic_regression": logistic_regression,
    "decision_tree": decision_tree,
    "random_forest": random_forest,
    "knn": knn,
    "svm": svm,
    "kernel_svm": kernel_svm
}

__all__ = ["MODEL_REGISTRY"]