import uuid
import re
import structlog
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.admin_message import AdminMessage
from app.services.storage_service import upload_file, get_signed_url
from app.exceptions import ValidationError

logger = structlog.get_logger()

router = APIRouter(prefix="/messages", tags=["messages"])

# ── File security ──────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp",  # images
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv",  # documents
    ".txt", ".rtf",                                      # text
}

BLOCKED_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".com", ".msi", ".scr", ".pif",  # Windows executables
    ".sh", ".bash", ".zsh", ".csh",                           # Shell scripts
    ".py", ".pyc", ".pyo", ".rb", ".pl", ".php",              # Script languages
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",             # JavaScript
    ".jar", ".class", ".war",                                  # Java
    ".dll", ".so", ".dylib",                                   # Libraries
    ".vbs", ".vbe", ".wsf", ".wsh", ".ps1", ".psm1",          # Windows scripting
    ".html", ".htm", ".svg", ".xml",                           # Can contain XSS
    ".iso", ".img", ".dmg",                                    # Disk images
    ".zip", ".rar", ".7z", ".tar", ".gz",                      # Archives (can hide malware)
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Dangerous byte signatures (magic bytes)
DANGEROUS_SIGNATURES = [
    b"MZ",           # Windows PE executable
    b"\x7fELF",      # Linux ELF executable
    b"#!/",          # Shell script
    b"<?php",        # PHP
    b"<script",      # HTML/JS injection
    b"%PDF-1",       # We allow PDF but check separately
]


def _sanitize_filename(name: str) -> str:
    """Remove path traversal, special chars, and normalize."""
    name = name.replace("\\", "/").split("/")[-1]  # strip path
    name = re.sub(r'[^\w\-. ()א-ת]', '_', name)    # keep safe chars + Hebrew
    name = name.strip(". ")
    if not name:
        name = "file"
    return name[:100]  # max 100 chars


def _get_extension(filename: str) -> str:
    if "." in filename:
        return "." + filename.rsplit(".", 1)[-1].lower()
    return ""


def _validate_file(filename: str, content: bytes) -> str:
    """Validate file safety. Returns sanitized filename or raises."""
    ext = _get_extension(filename)

    # Block dangerous extensions
    if ext in BLOCKED_EXTENSIONS:
        raise ValidationError(f"סוג קובץ {ext} אינו מורשה")

    # Only allow known safe extensions
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"סוג קובץ {ext} אינו נתמך. קבצים מורשים: תמונות, PDF, מסמכי Office, טקסט")

    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise ValidationError("קובץ גדול מדי — מקסימום 10MB")

    if len(content) == 0:
        raise ValidationError("קובץ ריק")

    # Check magic bytes — block executables disguised as images/docs
    header = content[:20].lower()
    if header.startswith(b"MZ") or header.startswith(b"\x7fELF"):
        logger.warning("blocked_executable_upload", filename=filename)
        raise ValidationError("קובץ חשוד — לא ניתן להעלות")
    if b"<script" in content[:1000].lower():
        logger.warning("blocked_script_injection", filename=filename)
        raise ValidationError("קובץ חשוד — לא ניתן להעלות")
    if content[:5] == b"#!/" or content[:5] == b"<?php":
        logger.warning("blocked_script_upload", filename=filename)
        raise ValidationError("קובץ חשוד — לא ניתן להעלות")

    return _sanitize_filename(filename)


# ── Attachment upload ──────────────────────────────────────────────────────────

CONTENT_TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp",
    ".pdf": "application/pdf",
    ".doc": "application/msword", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".csv": "text/csv", ".txt": "text/plain", ".rtf": "application/rtf",
}


@router.post("/upload-attachment")
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a file attachment for messages. Returns the storage key and signed URL."""
    content = await file.read()
    safe_name = _validate_file(file.filename or "file", content)
    ext = _get_extension(safe_name)
    content_type = CONTENT_TYPES.get(ext, "application/octet-stream")

    # Store under messages/ prefix with unique ID
    file_id = str(uuid.uuid4())[:12]
    storage_key = f"messages/{current_user.id}/{file_id}_{safe_name}"

    await upload_file(content, storage_key, content_type)
    signed_url = await get_signed_url(storage_key, expires=86400 * 7)  # 7 days

    logger.info("message_attachment_uploaded", user_id=str(current_user.id), filename=safe_name, size=len(content))

    return {
        "key": storage_key,
        "name": safe_name,
        "url": signed_url,
        "size": len(content),
        "content_type": content_type,
    }


# ── Message dict helper ───────────────────────────────────────────────────────

def _msg_dict(m):
    return {
        "id": str(m.id),
        "subject": m.subject,
        "body": m.body,
        "category": m.category,
        "direction": m.direction,
        "is_read": m.is_read,
        "thread_id": str(m.thread_id) if m.thread_id else None,
        "attachments": m.attachments or [],
        "created_at": m.created_at.isoformat(),
        "user_name": m.user_name,
    }


# ── Thread endpoints ──────────────────────────────────────────────────────────

@router.get("/threads")
async def get_user_threads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    all_msgs = (await db.execute(
        select(AdminMessage)
        .where(AdminMessage.user_id == current_user.id)
        .order_by(AdminMessage.created_at.asc())
    )).scalars().all()

    threads: dict[str, list] = {}
    for m in all_msgs:
        tid = str(m.thread_id) if m.thread_id else str(m.id)
        threads.setdefault(tid, []).append(m)

    result = []
    for tid, msgs in threads.items():
        first = msgs[0]
        last = msgs[-1]
        unread = sum(1 for m in msgs if not m.is_read and m.direction == "outbound")
        result.append({
            "thread_id": tid,
            "subject": first.subject,
            "category": first.category,
            "message_count": len(msgs),
            "unread_count": unread,
            "last_message": _msg_dict(last),
            "last_activity": last.created_at.isoformat(),
        })
    result.sort(key=lambda t: t["last_activity"], reverse=True)
    return result


@router.get("/thread/{thread_id}")
async def get_thread_messages(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    msgs = (await db.execute(
        select(AdminMessage).where(
            AdminMessage.user_id == current_user.id,
            (AdminMessage.thread_id == thread_id) | (AdminMessage.id == thread_id),
        ).order_by(AdminMessage.created_at.asc())
    )).scalars().all()
    for m in msgs:
        if not m.is_read and m.direction == "outbound":
            m.is_read = True
    await db.commit()
    return [_msg_dict(m) for m in msgs]


@router.get("/inbox")
async def get_inbox(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(AdminMessage)
        .where(AdminMessage.user_id == current_user.id, AdminMessage.direction == "outbound")
        .order_by(AdminMessage.created_at.desc())
        .limit(50)
    )
    msgs = (await db.execute(stmt)).scalars().all()
    return [_msg_dict(m) for m in msgs]


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = (await db.execute(
        select(func.count()).select_from(AdminMessage).where(
            AdminMessage.user_id == current_user.id,
            AdminMessage.direction == "outbound",
            AdminMessage.is_read == False,  # noqa
        )
    )).scalar() or 0
    return {"unread": count}


@router.put("/{message_id}/read")
async def mark_read(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    msg = (await db.execute(
        select(AdminMessage).where(
            AdminMessage.id == message_id,
            AdminMessage.user_id == current_user.id,
        )
    )).scalar_one_or_none()
    if msg:
        msg.is_read = True
        await db.commit()
    return {"ok": True}
