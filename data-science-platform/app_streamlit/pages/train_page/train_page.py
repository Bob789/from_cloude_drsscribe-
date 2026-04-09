# File: app_streamlit/pages/train_page.py
"""
Train page for uploading CSV and training ML models.

This module provides the UI for model training configuration and execution.
"""

import streamlit as st
import pandas as pd
from components.api_client import APIClient
from pages.train_page.metrics_display import display_classification_metrics, display_regression_metrics

api_client = APIClient()

CLASSIFICATION_MODELS = ["logistic_regression", "decision_tree", "random_forest", "knn", "svm", "kernel_svm"]
MODEL_LABELS = {
    "linear_regression": "Linear Regression (Continuous Target)",
    "logistic_regression": "Logistic Regression (Classification)",
    "decision_tree": "Decision Tree (Classification)",
    "random_forest": "Random Forest (Classification)",
    "knn": "K-Nearest Neighbors (Classification)",
    "svm": "Support Vector Machine (Linear)",
    "kernel_svm": "Kernel SVM (RBF)"
}


def show():
    """Display the model training page."""
    st.title("Train Model")
    st.write("Upload a CSV file and configure training parameters.")
    st.info("Training a model costs **1 token**")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is None:
        _show_example_format()
        return

    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df.head(10), width='stretch')
    st.write(f"**Shape:** {df.shape[0]} rows x {df.shape[1]} columns")

    st.subheader("Configuration")
    all_columns = df.columns.tolist()

    col1, col2 = st.columns(2)
    with col1:
        feature_columns = st.multiselect("Select Feature Columns (X)", all_columns,
                                         default=all_columns[:-1] if len(all_columns) > 1 else [])
    with col2:
        label_column = st.selectbox("Select Label Column (y)", all_columns,
                                    index=len(all_columns) - 1 if all_columns else 0)

    st.write("### Model Configuration")
    model_type = st.selectbox("Model Type", list(MODEL_LABELS.keys()),
                              format_func=lambda x: MODEL_LABELS[x])

    col3, col4 = st.columns(2)
    with col3:
        model_name = st.text_input("Model Name",
                                   value=f"model_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}")
    with col4:
        test_size = st.slider("Test Set Size (%)", 10, 50, 20, 5) / 100

    st.write(f"**Features ({len(feature_columns)}):** {', '.join(feature_columns)}")
    st.write(f"**Label:** {label_column}")
    st.divider()

    if st.button("Train Model", type="primary"):
        _train_model(uploaded_file, model_name, feature_columns, label_column, test_size, model_type)


def _train_model(uploaded_file, model_name, feature_columns, label_column, test_size, model_type):
    """Execute model training with provided parameters."""
    if not feature_columns:
        st.error("Please select at least one feature column!")
        return
    if label_column in feature_columns:
        st.error("Label column cannot be in feature columns!")
        return
    if not model_name:
        st.error("Please provide a model name!")
        return

    uploaded_file.seek(0)
    with st.spinner("Training model..."):
        result = api_client.train_model(file=uploaded_file, model_name=model_name,
                                        feature_columns=",".join(feature_columns),
                                        label_column=label_column, test_size=test_size,
                                        model_type=model_type)

    if "error" in result:
        st.error(f"Training failed: {result['error']}")
        if result.get("status_code") == 402:
            st.warning("Insufficient tokens! Please purchase more tokens.")
        return

    st.success(f"Model '{model_name}' trained successfully!")
    st.subheader("Model Performance")

    metadata = result["metadata"]
    metrics = metadata["metrics"]
    eval_strategy = metadata.get("evaluation", {}).get("strategy", "holdout")
    is_classification = model_type in CLASSIFICATION_MODELS

    with st.expander("Debug: Raw Metrics"):
        st.json(metrics)
        st.write(f"**Evaluation Strategy:** {eval_strategy}")

    if is_classification:
        display_classification_metrics(metrics, eval_strategy)
    else:
        display_regression_metrics(metrics, eval_strategy)

    if "metrics_summary" in metadata:
        st.info(f"**Summary:** {metadata['metrics_summary']}")

    _update_token_balance()

    with st.expander("Preprocessing Details"):
        st.json(metadata["preprocessing"])


def _update_token_balance():
    """Update token balance after training."""
    username = st.session_state.get("username")
    if username:
        token_result = api_client.get_tokens(username)
        if "tokens" in token_result:
            st.session_state["tokens"] = token_result["tokens"]
            st.info(f"1 token deducted. Remaining: {token_result['tokens']} tokens")
        else:
            st.session_state["tokens"] -= 1
    else:
        st.session_state["tokens"] -= 1
    st.rerun()


def _show_example_format():
    """Display example CSV formats for users."""
    st.info("Upload a CSV file to get started")
    with st.expander("Example CSV Format"):
        st.write("**For Regression (Linear Regression):**")
        st.dataframe(pd.DataFrame({"feature1": [1, 2, 3, 4, 5], "feature2": [10, 20, 30, 40, 50],
                                   "target": [100, 200, 150, 250, 180]}))
        st.write("**For Classification:**")
        st.dataframe(pd.DataFrame({"feature1": [5.1, 4.9, 6.7, 5.8], "feature2": [3.5, 3.0, 3.1, 2.7],
                                   "species": ["setosa", "setosa", "versicolor", "virginica"]}))
        st.write("**Tips:** Use Linear Regression for continuous targets, Classification for categories.")