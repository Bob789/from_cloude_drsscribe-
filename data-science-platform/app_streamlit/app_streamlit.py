# File: Final_Project_v003/app_streamlit/app_streamlit.py
# streamlit run app_streamlit/app_streamlit.py

"""
app_streamlit.py
Main Streamlit interface for the Data Science Demo Platform.
Provides authentication and navigation to different pages.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add app_streamlit directory to path for local imports
app_streamlit_dir = Path(__file__).parent
sys.path.insert(0, str(app_streamlit_dir))

import streamlit as st
from app_fastapi import database_manager as db
from components.api_client import APIClient

# === Embedded Page Icon ===
from page_icon_embedded import get_icon_image, get_icon_data_url


# Ensure database and tables exist
db.create_database_if_not_exists()
db.create_users_table()
db.create_usage_logs_table()

# Initialize API client
api_client = APIClient()

# Page configuration
st.set_page_config(
    page_title="ML Platform",
    page_icon=get_icon_image(),  # Use embedded icon instead of emoji
    layout="wide"
)

def init_session_state():
    """Initialize session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "page" not in st.session_state:
        st.session_state["page"] = "Dashboard"

def login_page():
    """Display login/signup page."""

    # === Display title with embedded icon ===
    st.markdown(
        f"""
        <h1 style='display:flex; align-items:center; gap:12px;'>
            <img src='{get_icon_data_url()}' width='40'>
            Data Science Demo Platform
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.write("Welcome! Please login or create an account to continue.")

    # Check server status
    server_status = api_client.get_server_status()

    if server_status["status"] != "online":
        st.error("🔴 FastAPI Server is Offline")
        st.warning(server_status["message"])

        if "help" in server_status:
            with st.expander("📋 How to Start the Server"):
                st.code(server_status["help"], language="bash")
                st.info("Copy the command above and run it in a new terminal window.")

        if st.button("🔄 Retry Connection"):
            st.rerun()

        st.divider()
        st.info("💡 **Tip:** You need to run the FastAPI server before using this application. See instructions above.")
        return

    # Show online status
    st.success("🟢 Connected to FastAPI Server")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            result = api_client.login(username, password)
            if "error" in result:
                st.error(f"Login failed: {result['error']}")
            else:
                st.session_state["logged_in"] = True
                st.success("Login successful!")
                st.rerun()

    with tab2:
        st.subheader("Create Account")
        new_username = st.text_input("Username", key="signup_user")
        new_password = st.text_input("Password", type="password", key="signup_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Sign Up"):
            if new_password != confirm_password:
                st.error("Passwords do not match!")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters!")
            else:
                result = api_client.signup(new_username, new_password)
                if "error" in result:
                    st.error(f"Signup failed: {result['error']}")
                else:
                    st.success("Account created! You receive 10 free tokens. Please login.")

def main_app():
    """Display main application with navigation."""
    # Check server status
    if not api_client.check_server_health():
        st.error("FastAPI Server Connection Lost")
        st.warning("The FastAPI server is not responding. Please check if it's still running, If not restart the server.")

        if st.button("🔄 Retry Connection"):
            st.rerun()

        if st.button("🚪 Logout"):
            api_client.logout()
            st.session_state["logged_in"] = False
            st.rerun()

        st.stop()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.write(f"**User:** {st.session_state.get('username', 'N/A')}")
    st.sidebar.write(f"**Tokens:** {st.session_state.get('tokens', 0)}")

    # Server status indicator
    with st.sidebar:
        st.divider()
        st.caption("🟢 Server: Online")

    # Build navigation options based on user role
    nav_options = ["Dashboard", "Train Model", "Make Prediction"]

    # Only show Admin Panel to admin users
    if st.session_state.get("is_admin", False):
        nav_options.append("Admin Panel")

    # Page selection
    page = st.sidebar.radio(
        "Go to:",
        nav_options
    )

    # Logout button
    if st.sidebar.button("Logout"):
        api_client.logout()
        st.session_state["logged_in"] = False
        st.rerun()

    # Display selected page
    if page == "Dashboard":
        from pages import dashboard
        dashboard.show()
    elif page == "Train Model":
        from pages import train_page
        train_page.show()
    elif page == "Make Prediction":
        from pages import predict_page
        predict_page.show()
    elif page == "Admin Panel":
        from pages import admin_page
        admin_page.show()

def main():
    """Main application entry point."""
    init_session_state()

    if not st.session_state["logged_in"]:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()