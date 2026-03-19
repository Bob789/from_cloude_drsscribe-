from functools import wraps
from fastapi import Depends, HTTPException, status
from app.middleware.auth import get_current_user
from app.models.user import User, UserRole


def require_role(*roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role.value} not authorized. Required: {[r.value for r in roles]}",
            )
        return current_user
    return role_checker


require_admin = require_role(UserRole.admin)
require_doctor = require_role(UserRole.doctor, UserRole.admin)
require_any = require_role(UserRole.doctor, UserRole.admin, UserRole.receptionist)
