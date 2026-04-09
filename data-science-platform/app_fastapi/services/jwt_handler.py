# File: Final_Project_v003/app_fastapi/services/jwt_handler.py
"""
jwt_handler.py
Handles creation and verification of JWT tokens for authentication.
"""

from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import HTTPException
import jwt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === JWT Configuration from environment variables ===

JWT_CONFIG = {
    "SECRET_KEY": os.getenv("SECRET_KEY", "default-secret-key"),
    "ALGORITHM": os.getenv("ALGORITHM", "HS256"),
    "ACCESS_TOKEN_EXPIRE_MINUTES": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
}

def create_access_token(subject: str, roles: List[str]) -> str:
    """
    Creates a signed JWT token for the given user.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "roles": roles,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"])
    }
    token = jwt.encode(payload, JWT_CONFIG["SECRET_KEY"], algorithm=JWT_CONFIG["ALGORITHM"])
    return token


def decode_token(token: str):
    """
    Decodes and validates a JWT token.
    Raises HTTPException if token is invalid or expired.
    """
    try:
        decoded = jwt.decode(token, JWT_CONFIG["SECRET_KEY"], algorithms=[JWT_CONFIG["ALGORITHM"]])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Your session has expired (tokens last 3 weeks). Please login again to get a new token."
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")