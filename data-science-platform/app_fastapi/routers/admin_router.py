# File: app_fastapi/routers/admin_router.py
"""
Admin router for user management operations.

Handles admin-only endpoints for managing users and viewing usage logs.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app_fastapi.services import user_service, jwt_handler
from app_fastapi.services.auth_dependency import get_current_user
from app_fastapi.services.logger_service import log_registration
from app_fastapi import database_manager as db

router = APIRouter(tags=["Admin"])


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str
    password: str
    tokens: int = 10
    is_admin: bool = False


class UserUpdate(BaseModel):
    """Schema for updating user details."""
    new_username: Optional[str] = None
    new_password: Optional[str] = None
    new_tokens: Optional[int] = None
    new_is_admin: Optional[bool] = None


def require_admin(current_user: dict) -> None:
    """Verify that the current user has admin privileges."""
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/users")
def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users from the database. Admin only."""
    require_admin(current_user)
    return {"users": db.select_all_users()}


@router.post("/users")
def create_user_admin(user: UserCreate, current_user: dict = Depends(get_current_user)):
    """Create a new user with specified attributes. Admin only."""
    require_admin(current_user)
    try:
        hashed_password = user_service.hash_password(user.password)
        from app_fastapi.database_manager import get_connection
        INSERT_QUERY = """INSERT INTO users (user_name, user_password, tokens, is_admin)
            VALUES (%s, %s, %s, %s) ON CONFLICT (user_name) DO NOTHING RETURNING user_id"""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(INSERT_QUERY, (user.username, hashed_password, user.tokens, user.is_admin))
                result = cursor.fetchone()
                conn.commit()
                if not result:
                    raise HTTPException(status_code=400, detail=f"User '{user.username}' already exists")

        roles = ["user", "admin"] if user.is_admin else ["user"]
        access_token = jwt_handler.create_access_token(subject=user.username, roles=roles)
        log_registration(user.username, success=True)
        db.add_usage_log(current_user["sub"], "USER_CREATED", 0, "SUCCESS", f"Created '{user.username}'")
        return {"message": f"User '{user.username}' created", "username": user.username,
                "tokens": user.tokens, "is_admin": user.is_admin, "access_token": access_token}
    except HTTPException:
        raise
    except Exception as e:
        log_registration(user.username, success=False)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{username}")
def update_user_admin(username: str, user_update: UserUpdate,
                      current_user: dict = Depends(get_current_user)):
    """Update user details. Admin only."""
    require_admin(current_user)
    try:
        hashed = user_service.hash_password(user_update.new_password) if user_update.new_password else None
        success = db.update_user_full(username, new_username=user_update.new_username,
                                      new_password=hashed, new_tokens=user_update.new_tokens,
                                      new_is_admin=user_update.new_is_admin)
        if not success:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        db.add_usage_log(current_user["sub"], "USER_UPDATED", 0, "SUCCESS", f"Updated '{username}'")
        return {"message": f"User '{username}' updated",
                "username": user_update.new_username or username}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{username}")
def delete_user_admin(username: str, current_user: dict = Depends(get_current_user)):
    """Delete a user from the database. Admin only."""
    require_admin(current_user)
    if current_user["sub"] == username:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    try:
        result = db.delete_user(username)
        if "not found" in result.lower():
            raise HTTPException(status_code=404, detail=result)
        db.add_usage_log(current_user["sub"], "USER_DELETED", 0, "SUCCESS", f"Deleted '{username}'")
        return {"message": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage_logs")
def get_usage_logs_api(username: Optional[str] = None, limit: int = 50,
                       current_user: dict = Depends(get_current_user)):
    """Get usage logs. Admin can see all logs, regular users see only their own."""
    is_admin = "admin" in current_user.get("roles", [])
    if not is_admin and username and username != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Not authorized to view other users' logs")
    if not is_admin:
        username = current_user["sub"]
    try:
        logs = db.get_usage_logs(username, limit)
        logs_list = [{"log_id": l[0], "username": l[1], "action": l[2], "tokens_changed": l[3],
                      "status": l[4], "timestamp": l[5].isoformat() if l[5] else None,
                      "details": l[6]} for l in logs]
        return {"logs": logs_list, "count": len(logs_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
