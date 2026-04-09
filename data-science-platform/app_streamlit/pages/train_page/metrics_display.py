# File: app_streamlit/pages/train_page/metrics_display.py
"""
Metrics display module for training results visualization.

This module handles formatting and displaying model performance metrics
for both classification and regression models.
"""

import streamlit as st
import pandas as pd
import numpy as np


def display_classification_metrics(metrics: dict, eval_strategy: str):
    """
    Display classification model metrics.

    Args:
        metrics: Dictionary containing classification metrics.
        eval_strategy: Evaluation strategy used ('cv' or 'holdout').
    """
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    if eval_strategy == "cv":
        with col_m1:
            st.metric("Accuracy (CV)", f"{metrics.get('accuracy_mean', 0):.4f}")
        with col_m2:
            st.metric("Precision (CV)", f"{metrics.get('precision_weighted_mean', 0):.4f}")
        with col_m3:
            st.metric("Recall (CV)", f"{metrics.get('recall_weighted_mean', 0):.4f}")
        with col_m4:
            st.metric("F1 Score (CV)", f"{metrics.get('f1_weighted_mean', 0):.4f}")

        st.write("**Standard Deviations:**")
        cols = st.columns(4)
        cols[0].write(f"+/-{metrics.get('accuracy_std', 0):.4f}")
        cols[1].write(f"+/-{metrics.get('precision_weighted_std', 0):.4f}")
        cols[2].write(f"+/-{metrics.get('recall_weighted_std', 0):.4f}")
        cols[3].write(f"+/-{metrics.get('f1_weighted_std', 0):.4f}")
    else:
        with col_m1:
            st.metric("Accuracy", f"{metrics.get('test_accuracy', metrics.get('accuracy', 0)):.4f}")
        with col_m2:
            st.metric("Precision", f"{metrics.get('test_precision_weighted', metrics.get('precision', 0)):.4f}")
        with col_m3:
            st.metric("Recall", f"{metrics.get('test_recall_weighted', metrics.get('recall', 0)):.4f}")
        with col_m4:
            st.metric("F1 Score", f"{metrics.get('test_f1_weighted', metrics.get('f1', 0)):.4f}")

    _display_confusion_matrix(metrics)


def _display_confusion_matrix(metrics: dict):
    """Display confusion matrix if available in metrics."""
    if "confusion_matrix" not in metrics:
        return

    with st.expander("Confusion Matrix"):
        cm = np.array(metrics['confusion_matrix'])
        st.dataframe(pd.DataFrame(cm))

        st.write("**Heatmap:**")
        import matplotlib.pyplot as plt
        import seaborn as sns

        fig, ax = plt.subplots(figsize=(6, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        ax.set_title('Confusion Matrix')
        st.pyplot(fig)


def display_regression_metrics(metrics: dict, eval_strategy: str):
    """
    Display regression model metrics.

    Args:
        metrics: Dictionary containing regression metrics.
        eval_strategy: Evaluation strategy used ('cv' or 'holdout').
    """
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    if eval_strategy == "cv":
        with col_m1:
            st.metric("R2 Score (CV)", f"{metrics.get('r2_mean', 0):.4f}")
        with col_m2:
            st.metric("RMSE (CV)", f"{metrics.get('rmse_mean', 0):.4f}")
        with col_m3:
            st.metric("MAE (CV)", f"{metrics.get('mae_mean', 0):.4f}")
        with col_m4:
            if "baseline_rmse_mean" in metrics:
                st.metric("Baseline RMSE", f"{metrics.get('baseline_rmse_mean', 0):.4f}")

        st.write("**Standard Deviations:**")
        cols = st.columns(4)
        cols[0].write(f"+/-{metrics.get('r2_std', 0):.4f}")
        cols[1].write(f"+/-{metrics.get('rmse_std', 0):.4f}")
        cols[2].write(f"+/-{metrics.get('mae_std', 0):.4f}")
    else:
        with col_m1:
            st.metric("R2 Score", f"{metrics.get('test_r2', metrics.get('r2', 0)):.4f}")
        with col_m2:
            st.metric("RMSE", f"{metrics.get('test_rmse', metrics.get('rmse', 0)):.4f}")
        with col_m3:
            st.metric("MAE", f"{metrics.get('test_mae', metrics.get('mae', 0)):.4f}")
        with col_m4:
            st.metric("MSE", f"{metrics.get('test_mse', metrics.get('mse', 0)):.4f}")
