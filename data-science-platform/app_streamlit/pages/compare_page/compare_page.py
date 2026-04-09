# File: app_streamlit/pages/compare_page/compare_page.py
"""
Compare Models page — trains all applicable models on the same dataset
and displays a side-by-side performance comparison.
"""

import streamlit as st
import pandas as pd
from components.api_client import APIClient

api_client = APIClient()

MODEL_LABELS = {
    "linear_regression": "Linear Regression",
    "logistic_regression": "Logistic Regression",
    "decision_tree": "Decision Tree",
    "random_forest": "Random Forest",
    "knn": "K-Nearest Neighbors",
    "svm": "SVM (Linear)",
    "kernel_svm": "Kernel SVM (RBF)",
}


def show():
    """Display the model comparison page."""
    st.title("Compare Models")
    st.write("Upload a dataset and compare **all** applicable models side-by-side.")
    st.info("Comparison costs **1 token** and evaluates every model on the same data.")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], key="compare_upload")

    if uploaded_file is None:
        _show_instructions()
        return

    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)
    st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")

    all_columns = df.columns.tolist()

    col1, col2 = st.columns(2)
    with col1:
        feature_columns = st.multiselect(
            "Select Feature Columns (X)", all_columns,
            default=all_columns[:-1] if len(all_columns) > 1 else [])
    with col2:
        label_column = st.selectbox(
            "Select Label Column (y)", all_columns,
            index=len(all_columns) - 1 if all_columns else 0)

    col3, col4, col5 = st.columns(3)
    with col3:
        task_type = st.selectbox("Task Type", ["auto", "classification", "regression"],
                                 help="Auto-detect works in most cases")
    with col4:
        eval_strategy = st.selectbox("Evaluation", ["cv", "holdout"])
    with col5:
        cv_folds = st.slider("CV Folds", 2, 10, 5) if eval_strategy == "cv" else 5

    st.divider()

    if st.button("Compare All Models", type="primary"):
        _run_comparison(uploaded_file, feature_columns, label_column,
                        task_type, eval_strategy, cv_folds)


def _run_comparison(uploaded_file, feature_columns, label_column,
                    task_type, eval_strategy, cv_folds):
    """Execute comparison and display results."""
    if not feature_columns:
        st.error("Please select at least one feature column!")
        return
    if label_column in feature_columns:
        st.error("Label column cannot be in feature columns!")
        return

    uploaded_file.seek(0)
    with st.spinner("Training and evaluating all models... This may take a moment."):
        result = api_client.compare_models(
            file=uploaded_file,
            feature_columns=",".join(feature_columns),
            label_column=label_column,
            evaluation_strategy=eval_strategy,
            cv_folds=cv_folds,
            task_type=task_type,
        )

    if "error" in result:
        st.error(f"Comparison failed: {result['error']}")
        if result.get("status_code") == 402:
            st.warning("Insufficient tokens! Please purchase more tokens.")
        return

    task = result.get("task_type", "classification")
    models_results = result.get("results", [])
    best_model = result.get("best_model")

    st.balloons()
    st.success(f"Compared **{len(models_results)}** {task} models. "
               f"Best model: **{MODEL_LABELS.get(best_model, best_model)}**")

    # Build comparison table
    if task == "classification":
        _show_classification_comparison(models_results, best_model, eval_strategy)
    else:
        _show_regression_comparison(models_results, best_model, eval_strategy)

    _update_token_balance()


def _show_classification_comparison(results, best_model, eval_strategy):
    """Display classification model comparison."""
    rows = []
    for r in results:
        m = r["metrics"]
        is_cv = eval_strategy == "cv"
        rows.append({
            "Model": MODEL_LABELS.get(r["model_type"], r["model_type"]),
            "Accuracy": m.get("accuracy_mean" if is_cv else "test_accuracy", 0),
            "Precision": m.get("precision_mean" if is_cv else "test_precision", 0),
            "Recall": m.get("recall_mean" if is_cv else "test_recall", 0),
            "F1 Score": m.get("f1_mean" if is_cv else "test_f1", 0),
            "Status": r["status"],
            "_type": r["model_type"],
        })

    df = pd.DataFrame(rows)
    successful = df[df["Status"] == "success"].copy()

    if successful.empty:
        st.error("All models failed to train.")
        return

    # Highlight best
    st.subheader("Performance Comparison")

    display_df = successful[["Model", "Accuracy", "Precision", "Recall", "F1 Score"]].copy()
    for col in ["Accuracy", "Precision", "Recall", "F1 Score"]:
        display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Bar chart
    st.subheader("Visual Comparison")
    chart_df = successful[["Model", "Accuracy", "F1 Score"]].set_index("Model")
    st.bar_chart(chart_df)

    # Best model highlight
    best_row = successful[successful["_type"] == best_model].iloc[0]
    st.success(
        f"**Best Model: {best_row['Model']}** — "
        f"Accuracy: {best_row['Accuracy']:.4f} | F1: {best_row['F1 Score']:.4f}"
    )


def _show_regression_comparison(results, best_model, eval_strategy):
    """Display regression model comparison."""
    rows = []
    for r in results:
        m = r["metrics"]
        is_cv = eval_strategy == "cv"
        rows.append({
            "Model": MODEL_LABELS.get(r["model_type"], r["model_type"]),
            "R²": m.get("r2_mean" if is_cv else "test_r2", 0),
            "RMSE": m.get("rmse_mean" if is_cv else "test_rmse", 0),
            "MAE": m.get("mae_mean" if is_cv else "test_mae", 0),
            "Status": r["status"],
            "_type": r["model_type"],
        })

    df = pd.DataFrame(rows)
    successful = df[df["Status"] == "success"].copy()

    if successful.empty:
        st.error("All models failed to train.")
        return

    st.subheader("Performance Comparison")

    display_df = successful[["Model", "R²", "RMSE", "MAE"]].copy()
    for col in ["R²", "RMSE", "MAE"]:
        display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Bar chart
    st.subheader("Visual Comparison")
    chart_df = successful[["Model", "R²"]].set_index("Model")
    st.bar_chart(chart_df)

    best_row = successful[successful["_type"] == best_model].iloc[0]
    st.success(
        f"**Best Model: {best_row['Model']}** — "
        f"R²: {best_row['R²']:.4f} | RMSE: {best_row['RMSE']:.4f}"
    )


def _update_token_balance():
    """Update token balance after comparison."""
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


def _show_instructions():
    """Display usage instructions."""
    st.info("Upload a CSV file to get started")
    with st.expander("How it works"):
        st.markdown("""
        1. **Upload** a CSV dataset
        2. **Select** feature columns and the target column
        3. **Click** "Compare All Models"
        4. The system will train **all** applicable models (classification or regression)
           and show you a side-by-side comparison
        5. The **best model** is highlighted automatically

        **Classification models:** Logistic Regression, Decision Tree, Random Forest, KNN, SVM, Kernel SVM

        **Regression models:** Linear Regression
        """)
