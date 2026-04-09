# File: app_fastapi/routers/auth_router.py
"""
Authentication router for user signup, login, and token management.

This module handles user authentication including registration, login,
JWT token generation, and token balance operations.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app_fastapi.services import user_service, jwt_handler
from app_fastapi.services.auth_dependency import get_current_user
from app_fastapi import database_manager as db
from app_fastapi.services.logger_service import log_registration, log_login, log_token_operation

router = APIRouter(tags=["Authentication"])


class UserLogin(BaseModel):
    """Schema for user login credentials."""
    username: str
    password: str


class TokenAdd(BaseModel):
    """Schema for adding tokens to a user account."""
    username: str
    tokens: int


@router.post("/signup")
def signup(user: UserLogin):
    """
    Register a new user account.

    Args:
        user: Login credentials for the new user.

    Returns:
        dict: Success message with initial token count.
    """
    if len(user.username) < 3 or " " in user.username:
        raise HTTPException(status_code=400,
                            detail="Username must be at least 3 characters and contain no spaces.")
    if len(user.password) < 6:
        raise HTTPException(status_code=400,
                            detail="Password must be at least 6 characters.")
    try:
        user_service.create_user(user.username, user.password)
        log_registration(user.username, success=True)
        return {"message": "User created successfully.", "tokens": 10}
    except Exception as e:
        log_registration(user.username, success=False)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def login(user: UserLogin):
    """
    Authenticate user and return JWT token.

    Args:
        user: Login credentials.

    Returns:
        dict: Access token, user info, and token balance.
    """
    db_user = db.get_user_by_name(user.username)
    if not db_user or not user_service.verify_password(user.password, db_user[2]):
        log_login(user.username, success=False)
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    log_login(user.username, success=True)

    roles = ["user"]
    if db_user[4]:
        roles.append("admin")

    access_token = jwt_handler.create_access_token(subject=user.username, roles=roles)

    return {"access_token": access_token, "token_type": "bearer", "username": user.username,
            "tokens": db_user[3], "is_admin": db_user[4]}


@router.get("/tokens/{username}")
def get_tokens(username: str, current_user: dict = Depends(get_current_user)):
    """
    Get token balance for a user.

    Args:
        username: Username to check balance for.
        current_user: Authenticated user from JWT.

    Returns:
        dict: Username and token balance.
    """
    if current_user["sub"] != username and "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Not authorized to view other users' tokens")

    tokens = db.get_user_tokens(username)
    if tokens is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "tokens": tokens}


@router.post("/add_tokens")
def add_tokens(token_request: TokenAdd, current_user: dict = Depends(get_current_user)):
    """
    Add tokens to a user account (simulates purchase).

    Args:
        token_request: Username and token amount to add.
        current_user: Authenticated user from JWT.

    Returns:
        dict: Success message and new balance.
    """
    if token_request.tokens <= 0:
        raise HTTPException(status_code=400, detail="Token amount must be positive")

    if current_user["sub"] != token_request.username and "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Not authorized to add tokens to other accounts")

    success = db.update_user_tokens(token_request.username, token_request.tokens)

    if not success:
        log_token_operation(token_request.username, "add", token_request.tokens, success=False)
        raise HTTPException(status_code=404, detail="User not found or update failed")

    log_token_operation(token_request.username, "add", token_request.tokens, success=True)
    db.add_usage_log(token_request.username, "TOKEN_PURCHASE", token_request.tokens,
                     "SUCCESS", f"Added {token_request.tokens} tokens")

    new_balance = db.get_user_tokens(token_request.username)
    return {"message": f"Successfully added {token_request.tokens} tokens", "new_balance": new_balance}


@router.get("/secure")
def secure_route(current_user: dict = Depends(get_current_user)):
    """
    Protected route example requiring valid JWT token.

    Args:
        current_user: Authenticated user from JWT.

    Returns:
        dict: Welcome message and token info.
    """
    return {"message": f"Welcome {current_user['sub']}!", "roles": current_user.get("roles", []),
            "issued_at": current_user["iat"], "expires_at": current_user["exp"]}


@router.get("/ping")
async def ping_auth():
    """Health check endpoint for auth router."""
    return {"message": "auth_router is active"}
