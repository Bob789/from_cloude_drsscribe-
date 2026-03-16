"""Encrypt/decrypt medical text fields (summaries, transcriptions).

Fields are encrypted with AES-256-GCM using the master ENCRYPTION_KEY.
Encrypted values are base64-encoded and always > 50 chars, which lets us
distinguish them from plaintext legacy data during migration.
"""
from app.utils.encryption import encrypt_field, decrypt_field
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Fields to encrypt in Summary model
SUMMARY_FIELDS = ("chief_complaint", "findings", "treatment_plan", "recommendations", "summary_text", "notes")

# Fields to encrypt in Transcription model
TRANSCRIPTION_FIELDS = ("full_text",)


def _is_encrypted(value: str | None) -> bool:
    """Heuristic: encrypted base64 values are always long."""
    if not value:
        return False
    return len(value) > 80 and " " not in value[:40]


def encrypt_summary_fields(summary) -> None:
    """Encrypt sensitive fields on a Summary ORM object in-place."""
    for field in SUMMARY_FIELDS:
        val = getattr(summary, field, None)
        if val and not _is_encrypted(val):
            try:
                setattr(summary, field, encrypt_field(val))
            except Exception as e:
                logger.error("encrypt_summary_failed", field=field, error=str(e))


def decrypt_summary_fields(summary) -> None:
    """Decrypt sensitive fields on a Summary ORM object in-place."""
    for field in SUMMARY_FIELDS:
        val = getattr(summary, field, None)
        if val and _is_encrypted(val):
            try:
                setattr(summary, field, decrypt_field(val))
            except Exception as e:
                logger.error("decrypt_summary_failed", field=field, error=str(e))


def encrypt_transcription_fields(transcription) -> None:
    """Encrypt sensitive fields on a Transcription ORM object in-place."""
    for field in TRANSCRIPTION_FIELDS:
        val = getattr(transcription, field, None)
        if val and not _is_encrypted(val):
            try:
                setattr(transcription, field, encrypt_field(val))
            except Exception as e:
                logger.error("encrypt_transcription_failed", field=field, error=str(e))


def decrypt_transcription_fields(transcription) -> None:
    """Decrypt sensitive fields on a Transcription ORM object in-place."""
    for field in TRANSCRIPTION_FIELDS:
        val = getattr(transcription, field, None)
        if val and _is_encrypted(val):
            try:
                setattr(transcription, field, decrypt_field(val))
            except Exception as e:
                logger.error("decrypt_transcription_failed", field=field, error=str(e))
