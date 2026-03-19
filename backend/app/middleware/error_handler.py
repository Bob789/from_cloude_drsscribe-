import uuid
import traceback
import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions import AppError

logger = structlog.get_logger()


def _get_user_id(request: Request) -> str | None:
    if hasattr(request.state, "user_id"):
        return str(request.state.user_id)
    return None


async def app_error_handler(request: Request, exc: AppError):
    error_id = str(uuid.uuid4())[:8].upper()

    # Log full details server-side only
    logger.warning(
        "app_error",
        error_id=error_id,
        code=exc.code,
        internal_detail=exc.detail,  # never sent to client
        user_id=_get_user_id(request),
        method=request.method,
        path=request.url.path,  # path only, no query params with tokens
    )

    # Client sees only: error_id + code + Hebrew message
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_id": error_id,
            "code": exc.code,
            "message": exc.message_he,
        },
    )


async def global_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())[:8].upper()

    # Full details logged server-side only
    logger.error(
        "unhandled_exception",
        error_id=error_id,
        user_id=_get_user_id(request),
        method=request.method,
        path=request.url.path,
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        traceback=traceback.format_exc(),
    )

    # Client sees generic message + error_id for support reference
    return JSONResponse(
        status_code=500,
        content={
            "error_id": error_id,
            "code": "ERR-5001",
            "message": "אירעה שגיאה במערכת. פנה לתמיכה עם מספר השגיאה.",
        },
    )
