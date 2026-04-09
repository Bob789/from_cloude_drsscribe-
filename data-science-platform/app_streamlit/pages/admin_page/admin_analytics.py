# File: app_streamlit/pages/admin_page/admin_analytics.py
"""
Admin analytics module for the admin panel.

This module handles token distribution visualization, usage logs display,
and trained models management.
"""

import streamlit as st
import pandas as pd
from components.api_client import APIClient

api_client = APIClient()


def show_token_distribution():
    """
    Display token distribution charts and statistics.

    Shows a bar chart of token balances across all users
    and calculates summary statistics.
    """
    try:
        result = api_client.get_all_users()

        if "error" in result:
            st.error(f"Failed to load token distribution: {result['error']}")
            return

        users = result.get("users", [])

        if users and len(users) > 0:
            df_users = pd.DataFrame(
                users,
                columns=["ID", "Username", "Password (Hashed)", "Tokens", "Is Admin", "Created At"]
            )
            df_users["Tokens"] = pd.to_numeric(df_users["Tokens"], errors='coerce').fillna(0).astype(int)

            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.bar_chart(df_users.set_index("Username")["Tokens"])

            with col_chart2:
                st.subheader("Statistics")
                st.write(f"**Mean:** {df_users['Tokens'].mean():.2f}")
                st.write(f"**Median:** {df_users['Tokens'].median():.2f}")
                st.write(f"**Max:** {df_users['Tokens'].max()}")
                st.write(f"**Min:** {df_users['Tokens'].min()}")
        else:
            st.info("No user data available for token distribution.")

    except Exception as e:
        st.error(f"Failed to load token distribution: {str(e)}")


def show_usage_logs():
    """
    Display system activity logs with filtering options.

    Shows recent activity logs including model training, predictions,
    and token purchases. Provides filtering by action type.
    """
    try:
        result = api_client.get_usage_logs(username=None, limit=50)

        if "error" in result:
            st.error(f"Failed to load usage logs: {result['error']}")
            return

        logs = result.get("logs", [])

        if logs:
            df_logs = pd.DataFrame(logs)
            df_logs = df_logs.rename(columns={
                "log_id": "ID",
                "username": "Username",
                "action": "Action",
                "tokens_changed": "Tokens Changed",
                "status": "Status",
                "timestamp": "Timestamp",
                "details": "Details"
            })
            df_logs = df_logs[["Timestamp", "Username", "Action", "Tokens Changed", "Status"]]
            df_logs["Timestamp"] = pd.to_datetime(df_logs["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

            action_filter = st.multiselect(
                "Filter by action type",
                options=df_logs["Action"].unique(),
                default=df_logs["Action"].unique()
            )

            filtered_logs = df_logs[df_logs["Action"].isin(action_filter)]
            st.dataframe(filtered_logs, width='stretch')

            st.subheader("Activity Summary")
            col_act1, col_act2, col_act3, col_act4 = st.columns(4)

            with col_act1:
                train_count = len(df_logs[df_logs["Action"] == "MODEL_TRAINING"])
                st.metric("Total Trainings", train_count)

            with col_act2:
                predict_count = len(df_logs[df_logs["Action"] == "PREDICTION"])
                st.metric("Total Predictions", predict_count)

            with col_act3:
                purchase_count = len(df_logs[df_logs["Action"] == "TOKEN_PURCHASE"])
                st.metric("Token Purchases", purchase_count)

            with col_act4:
                user_actions = len(df_logs[df_logs["Action"].isin(
                    ["USER_CREATED", "USER_UPDATED", "USER_DELETED"]
                )])
                st.metric("User Management", user_actions)
        else:
            st.info("No activity logs available.")

    except Exception as e:
        st.error(f"Failed to load usage logs: {str(e)}")


def show_models_section():
    """
    Display trained models section with details and delete options.

    Shows all trained models with their configuration, performance metrics,
    and provides ability to delete models.
    """
    result = api_client.list_models()

    if "error" in result:
        st.error(f"Failed to load models: {result['error']}")
    elif "models" in result and result["models"]:
        st.write(f"Total models: {result['count']}")

        for model in result["models"]:
            with st.expander(f"{model['model_name']}"):
                col_m1, col_m2 = st.columns(2)

                with col_m1:
                    st.write(f"**Type:** {model.get('model_type', 'N/A')}")
                    st.write(f"**Features:** {', '.join(model.get('feature_columns', []))}")
                    st.write(f"**Label:** {model.get('label_column', 'N/A')}")

                with col_m2:
                    if "metrics" in model:
                        st.write("**Performance:**")
                        metrics = model['metrics']

                        r2_value = metrics.get('test_r2') or metrics.get('r2_mean') or metrics.get('r2')
                        rmse_value = metrics.get('test_rmse') or metrics.get('rmse_mean') or metrics.get('rmse')

                        if r2_value is not None:
                            st.write(f"- R2: {r2_value:.4f}")
                        if rmse_value is not None:
                            st.write(f"- RMSE: {rmse_value:.4f}")

                    st.write(f"**Trained:** {model.get('trained_at', 'N/A')}")

                if st.button(f"Delete {model['model_name']}", key=f"delete_{model['model_name']}"):
                    if st.button(f"Confirm delete {model['model_name']}?", key=f"confirm_{model['model_name']}"):
                        delete_result = api_client.delete_model(model['model_name'])
                        if "error" in delete_result:
                            st.error(f"Failed to delete: {delete_result['error']}")
                        else:
                            st.success(f"Model '{model['model_name']}' deleted!")
                            st.rerun()
    else:
        st.info("No models trained yet.")
