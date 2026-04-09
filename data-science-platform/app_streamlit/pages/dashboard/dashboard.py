# File: app_streamlit/pages/dashboard.py
"""
Dashboard page showing user stats, token balance, and usage history.

This module provides the main dashboard view with token balance,
model list, and activity history.
"""

import streamlit as st
import pandas as pd
from components.api_client import APIClient
from pages.dashboard.purchase_form import show_purchase_form

api_client = APIClient()


def show():
    """Display the main dashboard page."""
    st.title("Dashboard")

    username = st.session_state.get("username")

    st.header("Token Balance")
    col1, col2, col3 = st.columns(3)
    col1.metric("Available Tokens", st.session_state.get("tokens", 0))
    col2.metric("Training Cost", "1 token/model")
    col3.metric("Prediction Cost", "5 tokens/request")

    show_purchase_form(username)

    st.divider()
    _show_models_section()

    st.divider()
    logs_data = _show_activity_section(username)

    st.divider()
    _show_quick_stats(logs_data)


def _show_models_section():
    """Display trained models section."""
    st.header("Your Models")
    result = api_client.list_models()

    if "error" in result:
        st.error(f"Failed to load models: {result['error']}")
        return

    if not result.get("models"):
        st.info("No models trained yet. Go to 'Train Model' to create your first model!")
        return

    st.write(f"You have {result['count']} trained model(s)")

    for model in result["models"]:
        with st.expander(f"{model['model_name']}"):
            col_m1, col_m2 = st.columns(2)

            with col_m1:
                st.write(f"**Type:** {model.get('model_type', 'N/A')}")
                features = model.get("feature_columns", model.get("original_features", []))
                st.write(f"**Features:** {', '.join(features) if features else 'N/A'}")
                st.write(f"**Label:** {model.get('label_column', 'N/A')}")

            with col_m2:
                if "metrics" in model:
                    _display_model_metrics(model["metrics"])
                eval_info = model.get("evaluation", {})
                if eval_info:
                    st.write(f"- Evaluation: {eval_info.get('strategy', 'N/A').upper()}")
                st.write(f"**Trained:** {model.get('created_at', model.get('trained_at', 'N/A'))}")


def _display_model_metrics(metrics):
    """Display model performance metrics."""
    st.write("**Performance Metrics:**")
    r2 = metrics.get("r2") or metrics.get("test_r2") or metrics.get("r2_mean")
    if r2 is not None:
        st.write(f"- R2 Score: {r2:.4f}")

    rmse = metrics.get("rmse") or metrics.get("test_rmse") or metrics.get("rmse_mean")
    if rmse is not None:
        st.write(f"- RMSE: {abs(rmse):.4f}")

    mae = metrics.get("mae") or metrics.get("test_mae") or metrics.get("mae_mean")
    if mae is not None:
        st.write(f"- MAE: {abs(mae):.4f}")

    accuracy = metrics.get("accuracy") or metrics.get("test_accuracy") or metrics.get("accuracy_mean")
    if accuracy is not None:
        st.write(f"- Accuracy: {accuracy:.4f}")

    f1 = (metrics.get("f1") or metrics.get("test_f1") or metrics.get("test_f1_weighted") or
          metrics.get("f1_mean") or metrics.get("f1_weighted_mean"))
    if f1 is not None:
        st.write(f"- F1 Score: {f1:.4f}")


def _show_activity_section(username):
    """Display recent activity logs."""
    st.header("Recent Activity")
    try:
        result = api_client.get_usage_logs(username, limit=20)
        if "error" in result:
            st.error(f"Failed to load usage history: {result['error']}")
            return None

        logs_data = result.get("logs", [])
        if not logs_data:
            st.info("No activity yet. Start training models or making predictions!")
            return None

        df = pd.DataFrame(logs_data)
        df = df.rename(columns={"log_id": "ID", "username": "Username", "action": "Action",
                                "tokens_changed": "Tokens Changed", "status": "Status",
                                "timestamp": "Timestamp", "details": "Details"})
        df = df[["Timestamp", "Action", "Tokens Changed", "Status", "Details"]]
        df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        st.dataframe(df, width='stretch')
        return logs_data
    except Exception as e:
        st.error(f"Failed to load usage history: {str(e)}")
        return None


def _show_quick_stats(logs_data):
    """Display quick statistics from logs."""
    st.header("Quick Stats")
    if not logs_data:
        st.info("No statistics available yet.")
        return

    col_s1, col_s2, col_s3 = st.columns(3)
    train_count = sum(1 for log in logs_data if log["action"] == "MODEL_TRAINING")
    predict_count = sum(1 for log in logs_data if log["action"] == "PREDICTION")
    tokens_spent = abs(sum(log["tokens_changed"] for log in logs_data if log["tokens_changed"] < 0))

    col_s1.metric("Models Trained", train_count)
    col_s2.metric("Predictions Made", predict_count)
    col_s3.metric("Tokens Spent", tokens_spent)