# File: app_fastapi/database/logging_operations.py
"""
Usage logging database operations module.

This module handles all usage log-related database operations
including creating logs, querying logs, and clearing logs.
"""

from .connection import get_connection


def create_usage_logs_table():
    """Create the usage_logs table for tracking token usage."""
    CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS usage_logs (
            log_id SERIAL PRIMARY KEY,
            user_name VARCHAR(50),
            action VARCHAR(100) NOT NULL,
            tokens_changed INTEGER DEFAULT 0,
            status VARCHAR(50) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (user_name) REFERENCES users(username) ON DELETE SET NULL
        )
    """
    CREATE_IDX_USER = """
        CREATE INDEX IF NOT EXISTS idx_usage_logs_user_name ON usage_logs (user_name)
    """
    CREATE_IDX_TS = """
        CREATE INDEX IF NOT EXISTS idx_usage_logs_timestamp ON usage_logs (timestamp DESC)
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_TABLE)
            cursor.execute(CREATE_IDX_USER)
            cursor.execute(CREATE_IDX_TS)
            conn.commit()
            print("Table 'usage_logs' created or already exists.")


def add_usage_log(user_name: str, action: str, tokens_changed: int,
                  status: str, details: str = None):
    """
    Log a usage event to the usage_logs table.

    Args:
        user_name: Username performing the action.
        action: Type of action performed.
        tokens_changed: Number of tokens changed (positive or negative).
        status: Status of the operation (SUCCESS, FAILED, etc.).
        details: Additional details about the operation.
    """
    INSERT_QUERY = """INSERT INTO usage_logs (user_name, action, tokens_changed, status, details)
        VALUES (%s, %s, %s, %s, %s)"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(INSERT_QUERY, (user_name, action, tokens_changed, status, details))
            conn.commit()


def get_usage_logs(user_name: str = None, limit: int = 50):
    """
    Get usage logs, optionally filtered by username.

    Args:
        user_name: Optional username filter.
        limit: Maximum number of logs to return.

    Returns:
        List of log tuples.
    """
    if user_name:
        query = """SELECT log_id, user_name, action, tokens_changed, status, timestamp, details
            FROM usage_logs WHERE user_name = %s ORDER BY timestamp DESC LIMIT %s"""
        params = (user_name, limit)
    else:
        query = """SELECT log_id, user_name, action, tokens_changed, status, timestamp, details
            FROM usage_logs ORDER BY timestamp DESC LIMIT %s"""
        params = (limit,)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


def clear_usage_logs():
    """Clear all usage logs from the database."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM usage_logs")
            conn.commit()
            print("All usage logs cleared.")
