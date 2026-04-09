# File: app_fastapi/database/connection.py
"""
Database connection management module.

This module handles PostgreSQL database connections including
automatic database creation and context-managed connection handling.
"""

import psycopg2
from psycopg2 import errors
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}


def connect_to_db(db_config: dict):
    """
    Create a database connection.

    Args:
        db_config: Dictionary containing database connection parameters.

    Returns:
        psycopg2 connection object or None if connection fails.
    """
    try:
        return psycopg2.connect(**db_config)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def create_database_if_not_exists():
    """Create the target database if it does not exist."""
    import re
    db_name = DB_CONFIG["dbname"]
    if not db_name or not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', db_name):
        print(f"Invalid database name: {db_name}")
        return

    try:
        conn = psycopg2.connect(
            dbname="postgres", user=DB_CONFIG["user"], password=DB_CONFIG["password"],
            host=DB_CONFIG["host"], port=DB_CONFIG["port"]
        )
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if not cursor.fetchone():
                from psycopg2 import sql
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                print(f"Database '{db_name}' created.")
            else:
                print(f"Database '{db_name}' already exists.")
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")


@contextmanager
def get_connection():
    """
    Context manager for PostgreSQL database connections.

    Automatically creates the database if it doesn't exist and ensures
    proper connection cleanup.

    Yields:
        psycopg2 connection object.
    """
    conn = None
    try:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
        except (psycopg2.OperationalError, errors.InvalidCatalogName):
            print(f"Database '{DB_CONFIG['dbname']}' not found. Creating...")
            create_database_if_not_exists()
            conn = psycopg2.connect(**DB_CONFIG)
        yield conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        if conn:
            conn.close()
