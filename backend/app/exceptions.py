class AppError(Exception):
    def __init__(self, code: str, message_he: str, status_code: int = 400, detail: str = None):
        self.code = code
        self.message_he = message_he
        self.status_code = status_code
        self.detail = detail


class NotFoundError(AppError):
    def __init__(self, entity: str, entity_id=None):
        super().__init__(
            code="NOT_FOUND",
            message_he=f"ה{entity} לא נמצא",
            status_code=404,
            detail=f"{entity} id={entity_id} not found" if entity_id else None,
        )


class ValidationError(AppError):
    def __init__(self, message_he: str, detail: str = None):
        super().__init__(code="VALIDATION_ERROR", message_he=message_he, status_code=422, detail=detail)


class DuplicateError(AppError):
    def __init__(self, field: str):
        super().__init__(code="DUPLICATE", message_he=f"הערך כבר קיים: {field}", status_code=409)


class StorageError(AppError):
    def __init__(self, detail: str):
        super().__init__(code="STORAGE_ERROR", message_he="שגיאה בשמירת קובץ", status_code=500, detail=detail)


class AIServiceError(AppError):
    def __init__(self, service: str, detail: str):
        super().__init__(code="AI_ERROR", message_he="שגיאה בשירות AI", status_code=502, detail=f"{service}: {detail}")


class AuthError(AppError):
    def __init__(self, message_he: str = "שגיאת הרשאה", detail: str = None):
        super().__init__(code="AUTH_ERROR", message_he=message_he, status_code=401, detail=detail)


class ForbiddenError(AppError):
    def __init__(self, message_he: str = "אין הרשאה לפעולה זו"):
        super().__init__(code="FORBIDDEN", message_he=message_he, status_code=403)
