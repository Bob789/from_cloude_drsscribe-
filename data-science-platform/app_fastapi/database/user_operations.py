# File: app_fastapi/database/user_operations.py
"""
User database operations module.

This module handles all user-related database operations including
CRUD operations, token management, and admin privilege handling.
"""

from .connection import get_connection


def create_users_table():
    """Create the users table if it does not exist."""
    CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            user_name VARCHAR(50) NOT NULL UNIQUE,
            user_password VARCHAR(255) NOT NULL,
            tokens INTEGER DEFAULT 0 CHECK (tokens >= 0),
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_TABLE)
            conn.commit()
            print("Table 'users' created or already exists.")


def select_all_users():
    """Fetch all users ordered by user_id."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY user_id ASC")
            return cursor.fetchall()


def add_user(user_name: str, user_password: str) -> str:
    """
    Register a new user in the database.

    Args:
        user_name: Username for the new user.
        user_password: Hashed password for the user.

    Returns:
        str: Success or failure message.
    """
    INSERT_QUERY = """INSERT INTO users (user_name, user_password)
        VALUES (%s, %s) ON CONFLICT (user_name) DO NOTHING"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(INSERT_QUERY, (user_name, user_password))
            conn.commit()
            if cursor.rowcount > 0:
                return f"User '{user_name}' registered successfully."
            return f"User '{user_name}' already exists."


def update_user(old_name: str, new_name: str) -> str:
    """Update an existing username."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET user_name = %s WHERE user_name = %s", (new_name, old_name))
            conn.commit()
            if cursor.rowcount > 0:
                return f"Username '{old_name}' updated to '{new_name}'."
            return f"User '{old_name}' not found."


def update_user_full(user_name: str, new_username: str = None, new_password: str = None,
                     new_tokens: int = None, new_is_admin: bool = None) -> bool:
    """
    Update user details. Only updates provided fields.

    Args:
        user_name: Current username.
        new_username: New username (optional).
        new_password: New hashed password (optional).
        new_tokens: New token balance (optional).
        new_is_admin: New admin status (optional).

    Returns:
        bool: True if update successful, False otherwise.
    """
    updates, params = [], []
    if new_username is not None:
        updates.append("user_name = %s")
        params.append(new_username)
    if new_password is not None:
        updates.append("user_password = %s")
        params.append(new_password)
    if new_tokens is not None:
        updates.append("tokens = %s")
        params.append(new_tokens)
    if new_is_admin is not None:
        updates.append("is_admin = %s")
        params.append(new_is_admin)

    if not updates:
        return False

    params.append(user_name)
    query = f"UPDATE users SET {', '.join(updates)} WHERE user_name = %s"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            conn.commit()
            return cursor.rowcount > 0


def delete_user(user_name: str) -> str:
    """Delete a user from the database."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE user_name = %s", (user_name,))
            conn.commit()
            if cursor.rowcount > 0:
                return f"User '{user_name}' deleted successfully."
            return f"User '{user_name}' not found."


def get_user_tokens(user_name: str) -> int:
    """Get the current token balance for a user."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT tokens FROM users WHERE user_name = %s", (user_name,))
            result = cursor.fetchone()
            return result[0] if result else None


def update_user_tokens(user_name: str, tokens_to_add: int) -> bool:
    """Update user token balance. Returns True if successful."""
    UPDATE_QUERY = """UPDATE users SET tokens = tokens + %s
        WHERE user_name = %s AND (tokens + %s) >= 0 RETURNING tokens"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(UPDATE_QUERY, (tokens_to_add, user_name, tokens_to_add))
            result = cursor.fetchone()
            conn.commit()
            return result is not None


def check_user_is_admin(user_name: str) -> bool:
    """Check if a user has admin privileges."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT is_admin FROM users WHERE user_name = %s", (user_name,))
            result = cursor.fetchone()
            return result[0] if result else False


def set_user_admin(user_name: str, is_admin: bool = True) -> str:
    """Set or remove admin privileges for a user."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET is_admin = %s WHERE user_name = %s RETURNING user_name",
                           (is_admin, user_name))
            result = cursor.fetchone()
            conn.commit()
            if result:
                status = "granted" if is_admin else "revoked"
                return f"Admin privileges {status} for user '{user_name}'."
            return f"User '{user_name}' not found."


def get_user_by_name(user_name: str):
    """Get user details including admin status by username."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, user_name, user_password, tokens, is_admin FROM users WHERE user_name = %s",
                (user_name,))
            return cursor.fetchone()
