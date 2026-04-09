# File: app_streamlit/pages/admin_page.py
"""
Admin page entry point for the admin panel.

This module provides the main navigation interface for the admin panel,
delegating to specialized modules for user management and analytics.
"""

import streamlit as st

from pages.admin_page.user_management import (
    show_users_table,
    show_create_user_form,
    show_update_user_form,
    show_delete_users_form
)
from pages.admin_page.admin_analytics import (
    show_token_distribution,
    show_usage_logs,
    show_models_section
)


def show():
    """
    Display the admin panel main page.

    Handles access control and provides navigation to different admin
    functions including user management and system analytics.
    """
    st.title("Admin Panel")

    is_admin = st.session_state.get("is_admin", False)

    if not is_admin:
        st.error("Access Denied")
        st.warning("You do not have administrator privileges to view this page.")
        st.info("Only administrators can access the admin panel.")
        return

    st.write("Comprehensive user management and system administration.")

    st.header("User Management")
    action = st.selectbox(
        "Select Action",
        ["View Users", "Create New User", "Update User", "Delete Users"],
        key="admin_action"
    )

    st.divider()

    if action == "View Users":
        show_users_table()
    elif action == "Create New User":
        show_create_user_form()
    elif action == "Update User":
        show_update_user_form()
    elif action == "Delete Users":
        show_delete_users_form()

    st.divider()

    st.header("Token Distribution")
    show_token_distribution()

    st.divider()

    st.header("System Activity Log")
    show_usage_logs()

    st.divider()

    st.header("Trained Models")
    show_models_section()