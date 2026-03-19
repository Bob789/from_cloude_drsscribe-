# ─── Error Codes Table ─────────────────────────────────────────────────────────
# Format: ERR-XXXX
#   1XXX — Authentication & authorization
#   2XXX — Validation & input
#   3XXX — Resource not found / conflict
#   4XXX — External service failures
#   5XXX — Internal server errors
#   9XXX — Rate limiting & abuse
#
# User sees: {"error_id": "A3F2B1C0", "code": "ERR-1001", "message": "..."}
# Server logs: full details with error_id for correlation
# ──────────────────────────────────────────────────────────────────────────────

ERROR_CODES: dict[str, dict] = {
    # ── Auth (1XXX) ──
    "ERR-1001": {"message_he": "נדרשת הזדהות", "status": 401},
    "ERR-1002": {"message_he": "טוקן לא תקין או פג תוקף", "status": 401},
    "ERR-1003": {"message_he": "אין הרשאה לפעולה זו", "status": 403},
    "ERR-1004": {"message_he": "המשתמש חסום", "status": 403},
    "ERR-1005": {"message_he": "שגיאה בהתחברות עם Google", "status": 401},
    "ERR-1006": {"message_he": "הפעלה פגה — יש להתחבר מחדש", "status": 401},

    # ── Validation (2XXX) ──
    "ERR-2001": {"message_he": "נתונים לא תקינים", "status": 422},
    "ERR-2002": {"message_he": "שדה חובה חסר", "status": 422},
    "ERR-2003": {"message_he": "פורמט לא תקין", "status": 422},
    "ERR-2004": {"message_he": "קובץ גדול מדי", "status": 413},
    "ERR-2005": {"message_he": "סוג קובץ לא נתמך", "status": 415},

    # ── Not Found / Conflict (3XXX) ──
    "ERR-3001": {"message_he": "הפריט לא נמצא", "status": 404},
    "ERR-3002": {"message_he": "המטופל לא נמצא", "status": 404},
    "ERR-3003": {"message_he": "הביקור לא נמצא", "status": 404},
    "ERR-3004": {"message_he": "ההקלטה לא נמצאה", "status": 404},
    "ERR-3005": {"message_he": "הערך כבר קיים", "status": 409},
    "ERR-3006": {"message_he": "המשתמש לא נמצא", "status": 404},
    "ERR-3007": {"message_he": "ההודעה לא נמצאה", "status": 404},

    # ── External Services (4XXX) ──
    "ERR-4001": {"message_he": "שגיאה בשירות AI — נסה שוב", "status": 502},
    "ERR-4002": {"message_he": "שגיאה בשמירת קובץ", "status": 502},
    "ERR-4003": {"message_he": "שגיאה בשירות Google", "status": 502},
    "ERR-4004": {"message_he": "שגיאה בשליחת מייל", "status": 502},
    "ERR-4005": {"message_he": "שירות חיצוני לא זמין — נסה שוב מאוחר יותר", "status": 503},

    # ── Internal (5XXX) ──
    "ERR-5001": {"message_he": "שגיאה פנימית במערכת", "status": 500},
    "ERR-5002": {"message_he": "שגיאה בבסיס הנתונים", "status": 500},
    "ERR-5003": {"message_he": "שגיאה בעיבוד הבקשה", "status": 500},

    # ── Rate Limiting (9XXX) ──
    "ERR-9001": {"message_he": "יותר מדי בקשות — נסה שוב בעוד דקה", "status": 429},
    "ERR-9002": {"message_he": "חריגה ממגבלת השימוש", "status": 429},
}


def get_error(code: str) -> dict:
    """Get error info by code. Returns safe defaults if code not found."""
    err = ERROR_CODES.get(code, {"message_he": "שגיאה לא מזוהה", "status": 500})
    return {"code": code, "message_he": err["message_he"], "status": err["status"]}
