from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_activity_log import UserActivityLog


async def log_activity(
    db: AsyncSession,
    user_id,
    action: str,
    entity_type: str = None,
    entity_id=None,
    description: str = None,
    metadata: dict = None,
    error_id: str = None,
    error_message: str = None,
    request: Request = None,
):
    log = UserActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        description=description,
        metadata_json=metadata,
        error_id=error_id,
        error_message=error_message,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    db.add(log)
    await db.commit()
