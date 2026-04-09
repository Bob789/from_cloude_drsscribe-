# File: Final_Project_v003/app_fastapi/services/user_service.py

from passlib.context import CryptContext
from app_fastapi.database_manager import connect_to_db, DB_CONFIG

# deprecated='auto'
# The system will allow using old algorithms if they're already in use (for backward compatibility)
# But will prefer newer algorithms when creating new connections
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    It's a function Encryption
    :param password:
    :return: str
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    It's a function that checks whether the password the user typed in plaintext form
    matches the encrypted version stored in the system
    :param plain_password:
    :param hashed_password:
    :return: bool
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_user(username: str, password: str):
    """
    Adds a new user to the database with hashed password
    :param username:
    :param password:
    :return: **None**
    """
    conn = connect_to_db(DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (user_name, user_password, tokens)
        VALUES (%s, %s, %s)
        """, (username, hash_password(password), 10))
    conn.commit()
    conn.close()

def find_user_by_username(username: str):
    """
    It's a function that find user by username
    :param username:
    :return: user record by username
    """
    conn = connect_to_db(DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT user_name, user_password, tokens FROM users WHERE user_name = %s", (username,))
    user = cur.fetchone()
    conn.close()
    return user