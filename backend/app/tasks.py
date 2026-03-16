import asyncio
import uuid
from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.transcription import Transcription, TranscriptionStatus
from app.models.recording import Recording
from app.models.recording_chunk import RecordingChunk
from app.models.summary import Summary, SummaryStatus
from app.models.visit import Visit
from app.services.whisper_service import transcribe_audio
from app.services.storage_service import get_s3_client
from app.services.llm_service import summarize_medical_visit
from app.utils.encryption import decrypt_audio
from app.services.pii_service import mask_pii, restore_pii, post_redact_dict
from app.services.tagging_service import extract_tags_from_summary, sync_diagnosis_tags
from app.utils.medical_encryption import encrypt_summary_fields, encrypt_transcription_fields
from app.config import settings
from sqlalchemy import select


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_transcription(self, recording_id: str):
    try:
        run_async(_process_transcription(recording_id, self))
    except Exception as exc:
        self.retry(exc=exc)


async def _process_transcription(recording_id: str, task):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Recording).where(Recording.id == uuid.UUID(recording_id)))
        recording = result.scalar_one_or_none()
        if not recording:
            return

        existing = await db.execute(select(Transcription).where(Transcription.recording_id == recording.id))
        transcription = existing.scalars().first()
        if transcription:
            transcription.status = TranscriptionStatus.processing
            transcription.error_message = None
        else:
            transcription = Transcription(recording_id=recording.id, status=TranscriptionStatus.processing)
            db.add(transcription)
        await db.commit()
        await db.refresh(transcription)

        try:
            client = get_s3_client()
            response = client.get_object(Bucket=settings.S3_BUCKET, Key=recording.audio_url)
            audio_data = response["Body"].read()
            if recording.encryption_key:
                audio_data = decrypt_audio(audio_data, recording.encryption_key)

            result_data = await transcribe_audio(audio_data)

            transcription.full_text = result_data["text"]
            transcription.speakers_json = result_data["segments"]
            transcription.language = result_data["language"]
            transcription.confidence_score = result_data["confidence"]
            transcription.status = TranscriptionStatus.done
            encrypt_transcription_fields(transcription)
            await db.commit()

            visit_result = await db.execute(select(Visit).join(Recording).where(Recording.id == recording.id))
            visit = visit_result.scalar_one_or_none()
            if visit:
                process_summary.delay(str(visit.id))
        except Exception as e:
            transcription.status = TranscriptionStatus.error
            transcription.error_message = str(e)
            await db.commit()
            raise


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_transcription_chunked(self, visit_id: str, recording_id: str):
    try:
        run_async(_process_transcription_chunked(visit_id, recording_id))
    except Exception as exc:
        self.retry(exc=exc)


async def _process_transcription_chunked(visit_id: str, recording_id: str):
    async with AsyncSessionLocal() as db:
        vid = uuid.UUID(visit_id)
        rid = uuid.UUID(recording_id)

        chunks_q = await db.execute(
            select(RecordingChunk)
            .where(RecordingChunk.visit_id == vid)
            .order_by(RecordingChunk.chunk_index)
        )
        chunks = chunks_q.scalars().all()
        if not chunks:
            return

        existing_trans = await db.execute(select(Transcription).where(Transcription.recording_id == rid))
        transcription = existing_trans.scalars().first()
        if transcription:
            transcription.status = TranscriptionStatus.processing
            transcription.error_message = None
        else:
            transcription = Transcription(recording_id=rid, status=TranscriptionStatus.processing)
            db.add(transcription)
        await db.commit()
        await db.refresh(transcription)

        try:
            client = get_s3_client()
            all_segments = []
            all_texts = []
            time_offset = 0.0
            total_confidence = 0.0

            for chunk in chunks:
                response = client.get_object(Bucket=settings.S3_BUCKET, Key=chunk.audio_url)
                audio_data = response["Body"].read()
                # Decrypt if encrypted
                if chunk.encryption_key:
                    audio_data = decrypt_audio(audio_data, chunk.encryption_key)

                chunk_result = await transcribe_audio(audio_data, filename=f"chunk_{chunk.chunk_index:04d}.webm")

                all_texts.append(chunk_result["text"])
                total_confidence += chunk_result["confidence"]

                for seg in chunk_result["segments"]:
                    all_segments.append({
                        "start": seg["start"] + time_offset,
                        "end": seg["end"] + time_offset,
                        "text": seg["text"],
                        "speaker": seg.get("speaker", "unknown"),
                    })

                if chunk_result["segments"]:
                    last_end = max(s["end"] for s in chunk_result["segments"])
                    time_offset += last_end
                elif chunk.duration_seconds:
                    time_offset += chunk.duration_seconds

                if chunk.duration_seconds is None and chunk_result["segments"]:
                    chunk.duration_seconds = max(s["end"] for s in chunk_result["segments"])
                    await db.commit()

            transcription.full_text = " ".join(all_texts)
            transcription.speakers_json = all_segments
            transcription.language = "he"
            transcription.confidence_score = total_confidence / len(chunks) if chunks else 0.0
            transcription.status = TranscriptionStatus.done
            encrypt_transcription_fields(transcription)
            await db.commit()

            process_summary.delay(visit_id)
        except Exception as e:
            transcription.status = TranscriptionStatus.error
            transcription.error_message = str(e)
            await db.commit()
            raise


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_summary(self, visit_id: str):
    try:
        run_async(_process_summary(visit_id))
    except Exception as exc:
        self.retry(exc=exc)


async def _process_summary(visit_id: str):
    async with AsyncSessionLocal() as db:
        vid = uuid.UUID(visit_id)
        result = await db.execute(select(Transcription).join(Recording).join(Visit).where(Visit.id == vid))
        transcription = result.scalar_one_or_none()
        if not transcription or not transcription.full_text:
            return

        existing_sum = await db.execute(select(Summary).where(Summary.visit_id == vid))
        summary = existing_sum.scalars().first()
        if summary:
            summary.status = SummaryStatus.processing
            summary.error_message = None
        else:
            summary = Summary(visit_id=vid, status=SummaryStatus.processing)
            db.add(summary)
        await db.commit()
        await db.refresh(summary)

        try:
            masked_text, pii_map = mask_pii(transcription.full_text)
            llm_result = await summarize_medical_visit(masked_text)

            text_fields = ["summary_text", "chief_complaint", "findings", "treatment_plan", "recommendations"]
            post_redact_dict(llm_result, text_fields)

            summary.summary_text = restore_pii(llm_result.get("summary_text", ""), pii_map)
            summary.chief_complaint = restore_pii(llm_result.get("chief_complaint", ""), pii_map)
            summary.findings = restore_pii(llm_result.get("findings", ""), pii_map)
            summary.diagnosis = llm_result.get("diagnosis", [])
            summary.treatment_plan = restore_pii(llm_result.get("treatment_plan", ""), pii_map)
            summary.recommendations = restore_pii(llm_result.get("recommendations", ""), pii_map)
            summary.urgency = llm_result.get("urgency", "low")
            summary.status = SummaryStatus.done
            # Tags need plaintext — extract before encryption
            await db.commit()
            await sync_diagnosis_tags(db, summary)
            await extract_tags_from_summary(db, summary)
            # Now encrypt medical data at rest
            encrypt_summary_fields(summary)
            await db.commit()
        except Exception as e:
            summary.status = SummaryStatus.error
            summary.error_message = str(e)
            await db.commit()
            raise
