from celery import chain
from app.tasks import process_transcription, process_summary
from app.services.status_service import update_pipeline_status


async def start_pipeline(recording_id: str, visit_id: str):
    await update_pipeline_status(visit_id, "uploading", 10)

    pipeline = chain(
        process_transcription.si(recording_id),
        process_summary.si(visit_id),
    )
    pipeline.apply_async()
    await update_pipeline_status(visit_id, "transcribing", 20)


async def get_pipeline_progress(visit_id: str) -> dict:
    from app.services.status_service import get_pipeline_status
    return await get_pipeline_status(visit_id)
