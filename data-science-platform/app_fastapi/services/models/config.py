# File: Final_Project_v003/app_fastapi/services/models/config.py
"""
Model Configuration - Defines all models in one place
"""
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import SVC, SVR

MODEL_CONFIG = {
    "linear_regression": {
        "estimator_class": LinearRegression,
        "default_params": {},
        "type": "regression",
        "needs_scaling": True,
        "supports_proba": False,
        "supports_random_state": False  # LinearRegression does not support random_state
    },
    "logistic_regression": {
        "estimator_class": LogisticRegression,
        "default_params": {"max_iter": 1000},
        "type": "classification",
        "needs_scaling": True,
        "supports_proba": True,
        "needs_label_encoding": True,
        "supports_random_state": True  # LogisticRegression supports random_state
    },
    "decision_tree": {
        "estimator_class": DecisionTreeClassifier,
        "default_params": {"max_depth": None, "criterion": "gini"},
        "type": "classification",
        "needs_scaling": False,
        "supports_proba": True,
        "needs_label_encoding": True,
        "supports_random_state": True  # DecisionTree supports random_state
    },
    "random_forest": {
        "estimator_class": RandomForestClassifier,
        "default_params": {"n_estimators": 100, "max_depth": None, "n_jobs": -1},
        "type": "classification",
        "needs_scaling": False,
        "supports_proba": True,
        "needs_label_encoding": True,
        "supports_random_state": True  # RandomForest supports random_state
    },
    "knn": {
        "estimator_class": KNeighborsClassifier,
        "default_params": {"n_neighbors": 5},
        "type": "classification",
        "needs_scaling": True,
        "supports_proba": True,
        "needs_label_encoding": True,
        "supports_random_state": False  # KNN does not support random_state (deterministic algorithm)
    },
    "svm": {
        "estimator_class": SVC,
        "default_params": {"kernel": "linear", "C": 1.0, "probability": True},
        "type": "classification",
        "needs_scaling": True,
        "supports_proba": True,
        "needs_label_encoding": True,
        "supports_random_state": True  # SVC supports random_state
    },
    "kernel_svm": {
        "estimator_class": SVC,
        "default_params": {"kernel": "rbf", "C": 1.0, "gamma": "scale", "probability": True},
        "type": "classification",
        "needs_scaling": True,
        "supports_proba": True,
        "needs_label_encoding": True,
        "supports_random_state": True  # SVC (kernel) supports random_state
    },
    "random_forest_regressor": {
        "estimator_class": RandomForestRegressor,
        "default_params": {"n_estimators": 100, "max_depth": None, "n_jobs": -1},
        "type": "regression",
        "needs_scaling": False,
        "supports_proba": False,
        "supports_random_state": True
    },
    "decision_tree_regressor": {
        "estimator_class": DecisionTreeRegressor,
        "default_params": {"max_depth": None},
        "type": "regression",
        "needs_scaling": False,
        "supports_proba": False,
        "supports_random_state": True
    },
    "knn_regressor": {
        "estimator_class": KNeighborsRegressor,
        "default_params": {"n_neighbors": 5},
        "type": "regression",
        "needs_scaling": True,
        "supports_proba": False,
        "supports_random_state": False
    },
    "svr": {
        "estimator_class": SVR,
        "default_params": {"kernel": "rbf", "C": 1.0, "gamma": "scale"},
        "type": "regression",
        "needs_scaling": True,
        "supports_proba": False,
        "supports_random_state": False
    }
}


def get_model_config(model_type: str) -> dict:
    """
    Returns configuration for a specific model
    """
    if model_type not in MODEL_CONFIG:
        raise ValueError(f"Unsupported model type: {model_type}. Supported: {list(MODEL_CONFIG.keys())}")

    return MODEL_CONFIG[model_type]