# File: Final_Project_v003/app_fastapi/services/auth_dependency.py
"""
Authentication dependency for protecting routes with JWT.
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app_fastapi.services import jwt_handler

# Define the security scheme for Swagger UI
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to extract and validate JWT token from Authorization header.
    Returns the decoded token claims (including username in 'sub' field).

    This uses HTTPBearer which automatically:
    - Shows the "Authorize" button in Swagger UI
    - Extracts the token from "Authorization: Bearer <token>"
    - Validates the format

    :returns
    current_user = {
    "sub": "Bob789",           # Subject - the username
    "exp": 1731067796,         # Expiration timestamp
    "iat": 1731064196,         # Issued at timestamp
    # Possibly other claims depending on your token creation
    }
    """
    token = credentials.credentials

    try:
        claims = jwt_handler.decode_token(token)
        return claims
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")