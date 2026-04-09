# File: app_streamlit/pages/admin_page/user_management.py
"""
User management module for admin panel user CRUD operations.
"""

import streamlit as st
import pandas as pd
from components.api_client import APIClient

api_client = APIClient()


def _get_users_dataframe(users):
    """Convert users list to formatted DataFrame."""
    df = pd.DataFrame(users, columns=["ID", "Username", "Password", "Tokens", "Is Admin", "Created At"])
    df = df[["ID", "Username", "Tokens", "Is Admin", "Created At"]]
    df["Tokens"] = pd.to_numeric(df["Tokens"], errors='coerce').fillna(0).astype(int)
    df["Is Admin"] = df["Is Admin"].apply(lambda x: "Yes" if x else "No")
    df["Created At"] = pd.to_datetime(df["Created At"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def show_users_table():
    """Display users table with statistics and filtering options."""
    try:
        result = api_client.get_all_users()
        if "error" in result:
            st.error(f"Failed to load users: {result['error']}")
            return

        users = result.get("users", [])
        if not users:
            st.info("No users found in the database.")
            return

        df_users = _get_users_dataframe(users)
        col1, col2 = st.columns([2, 1])
        with col1:
            threshold = st.slider("Show users with at least X tokens", 0, 100, 0)
        with col2:
            sort_by = st.selectbox("Sort by", ["ID", "Tokens", "Username"])

        filtered_df = df_users[df_users["Tokens"] >= threshold]
        filtered_df = filtered_df.sort_values(sort_by, ascending=sort_by != "Tokens")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Users", len(df_users))
        col_b.metric("Filtered Users", len(filtered_df))
        col_c.metric("Total Tokens", df_users["Tokens"].sum())
        st.dataframe(filtered_df, width='stretch')
    except Exception as e:
        st.error(f"Failed to load users: {str(e)}")


def show_create_user_form():
    """Display form for creating a new user with JWT token generation."""
    st.subheader("Create New User")
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", key="create_username")
            password = st.text_input("Password", type="password", key="create_password")
        with col2:
            tokens = st.number_input("Initial Tokens", min_value=0, value=10, step=1, key="create_tokens")
            is_admin = st.checkbox("Admin Privileges", key="create_is_admin")

        if st.form_submit_button("Create User", type="primary"):
            if not username or not password:
                st.error("Username and password are required.")
            else:
                with st.spinner("Creating user..."):
                    result = api_client.create_user_admin(username, password, tokens, is_admin)
                    if "error" in result:
                        st.error(f"Failed to create user: {result['error']}")
                    else:
                        st.success(f"User '{username}' created!")
                        with st.expander("Generated JWT Token"):
                            st.code(result.get("access_token", "N/A"))
                        st.balloons()


def show_update_user_form():
    """Display form for updating an existing user."""
    st.subheader("Update User")
    try:
        result = api_client.get_all_users()
        if "error" in result:
            st.error(f"Failed to load users: {result['error']}")
            return
        users = result.get("users", [])
        if not users:
            st.warning("No users available to update.")
            return

        usernames = [u[1] for u in users]
        selected = st.selectbox("Select User to Update", usernames, key="update_selectbox_main")
        user_data = next((u for u in users if u[1] == selected), None)
        if not user_data:
            st.error("Failed to load user data.")
            return

        prev = st.session_state.get("prev_selected_user")
        if prev != selected or "update_tokens" not in st.session_state:
            st.session_state.update_tokens = int(user_data[3])
            st.session_state.update_is_admin = bool(user_data[4])
            st.session_state.update_password = ""
            st.session_state.prev_selected_user = selected

        with st.form("update_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Password", type="password", key="update_password")
            with col2:
                st.number_input("Tokens", min_value=0, step=1, key="update_tokens")
                st.checkbox("Admin Privileges", key="update_is_admin")

            if st.form_submit_button("Update User", type="primary"):
                update_data = {"new_tokens": int(st.session_state.update_tokens),
                               "new_is_admin": bool(st.session_state.update_is_admin)}
                if st.session_state.update_password:
                    update_data["new_password"] = st.session_state.update_password
                result = api_client.update_user_admin(username=selected, **update_data)
                if "error" in result:
                    st.error(f"Failed to update user: {result['error']}")
                else:
                    st.success(f"User '{selected}' updated!")
                    st.rerun()
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")


def show_delete_users_form():
    """Display form for deleting users with checkboxes."""
    st.subheader("Delete Users")
    st.warning("WARNING: This action cannot be undone!")
    try:
        result = api_client.get_all_users()
        if "error" in result:
            st.error(f"Failed to load users: {result['error']}")
            return
        users = result.get("users", [])
        if not users:
            st.warning("No users available to delete.")
            return

        current_username = st.session_state.get("username", "")
        df = pd.DataFrame(users, columns=["ID", "Username", "Password", "Tokens", "Is Admin", "Created At"])
        df = df[["ID", "Username", "Tokens", "Is Admin"]]
        df["Is Admin"] = df["Is Admin"].apply(lambda x: "Yes" if x else "No")

        st.info(f"Note: You cannot delete your own account ({current_username})")
        users_to_delete = []
        for _, row in df.iterrows():
            username = row["Username"]
            is_self = username == current_username
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            with col1:
                if is_self:
                    st.checkbox("Select", key=f"del_{username}", disabled=True, value=False)
                elif st.checkbox("Select", key=f"del_{username}"):
                    users_to_delete.append(username)
            col2.write(f"**{username}**")
            col3.write(f"Tokens: {row['Tokens']}")
            col4.write(f"Admin: {row['Is Admin']}")

        st.divider()
        if users_to_delete:
            st.error(f"Deleting {len(users_to_delete)} user(s): {', '.join(users_to_delete)}")
            if st.button("Confirm Delete", type="primary"):
                success, errors = 0, 0
                for username in users_to_delete:
                    res = api_client.delete_user_admin(username)
                    if "error" in res:
                        st.error(f"Failed: {username}")
                        errors += 1
                    else:
                        success += 1
                if success:
                    st.success(f"Deleted {success} user(s)!")
                st.rerun()
        else:
            st.info("Select at least one user to delete.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
