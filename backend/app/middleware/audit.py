from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.database import AsyncSessionLocal
from app.services.audit_service import log_action

AUDIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        if request.method in AUDIT_METHODS and response.status_code < 400:
            try:
                user_id = None
                if hasattr(request.state, "user"):
                    user_id = request.state.user.id

                path_parts = request.url.path.strip("/").split("/")
                entity_type = path_parts[1] if len(path_parts) > 1 else "unknown"
                entity_id = path_parts[2] if len(path_parts) > 2 else None

                async with AsyncSessionLocal() as db:
                    await log_action(
                        db=db,
                        action=f"{request.method} {request.url.path}",
                        entity_type=entity_type,
                        entity_id=entity_id,
                        user_id=user_id,
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent"),
                    )
            except Exception:
                pass

        return response
