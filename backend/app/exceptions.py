class AppError(Exception):
    def __init__(self, code: str, message_he: str, status_code: int = 400, detail: str = None):
        self.code = code
        self.message_he = message_he
        self.status_code = status_code
        self.detail = detail  # internal only — never sent to client


class NotFoundError(AppError):
    def __init__(self, entity: str, entity_id=None):
        code_map = {"מטופל": "ERR-3002", "ביקור": "ERR-3003", "הקלטה": "ERR-3004", "משתמש": "ERR-3006", "הודעה": "ERR-3007"}
        error_code = code_map.get(entity, "ERR-3001")
        super().__init__(
            code=error_code,
            message_he=f"ה{entity} לא נמצא",
            status_code=404,
            detail=f"{entity} id={entity_id}" if entity_id else None,
        )


class ValidationError(AppError):
    def __init__(self, message_he: str, detail: str = None):
        super().__init__(code="ERR-2001", message_he=message_he, status_code=422, detail=detail)


class DuplicateError(AppError):
    def __init__(self, field: str):
        super().__init__(code="ERR-3005", message_he="הערך כבר קיים", status_code=409, detail=f"duplicate: {field}")


class StorageError(AppError):
    def __init__(self, detail: str):
        super().__init__(code="ERR-4002", message_he="שגיאה בשמירת קובץ", status_code=502, detail=detail)


class AIServiceError(AppError):
    def __init__(self, service: str, detail: str):
        super().__init__(code="ERR-4001", message_he="שגיאה בשירות AI — נסה שוב", status_code=502, detail=f"{service}: {detail}")


class AuthError(AppError):
    def __init__(self, message_he: str = "נדרשת הזדהות", detail: str = None):
        super().__init__(code="ERR-1001", message_he=message_he, status_code=401, detail=detail)


class ForbiddenError(AppError):
    def __init__(self, message_he: str = "אין הרשאה לפעולה זו"):
        super().__init__(code="ERR-1003", message_he=message_he, status_code=403)
