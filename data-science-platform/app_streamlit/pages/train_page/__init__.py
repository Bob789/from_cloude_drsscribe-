# File: app_streamlit/pages/train_page/__init__.py
"""
Train page package for model training functionality.

This package provides modular components for model training and metrics display.
"""

from .train_page import show
from .metrics_display import display_classification_metrics, display_regression_metrics

__all__ = ['show', 'display_classification_metrics', 'display_regression_metrics']