"""Tests for task pipeline logic (no DB, no Celery).

Covers: the decrypt→process→encrypt pipeline, _make_session factory.
"""
import pytest
from unittest.mock import MagicMock
from app.utils.medical_encryption import (
    encrypt_transcription_fields, decrypt_transcription_fields,
    encrypt_summary_fields, decrypt_summary_fields,
    _is_encrypted,
)


class TestTranscriptionPipeline:
    """Simulates the exact pipeline from tasks.py:
    1. Read encrypted transcription from DB
    2. Decrypt before LLM
    3. Process
    4. Encrypt summary
    5. Save
    """

    def test_full_pipeline_roundtrip(self):
        # Step 1: Simulate encrypted transcription in DB
        transcription = MagicMock()
        transcription.full_text = "רופא שלום מה מביא אותך? מטופל כאבים בחזה מאז הבוקר"
        encrypt_transcription_fields(transcription)
        assert _is_encrypted(transcription.full_text), "Should be encrypted in DB"

        # Step 2: Decrypt before LLM (the bug we fixed in INC-011)
        decrypt_transcription_fields(transcription)
        assert not _is_encrypted(transcription.full_text), "Should be plaintext for LLM"
        assert "כאבים בחזה" in transcription.full_text

        # Step 3: Simulate LLM result → summary
        summary = MagicMock()
        summary.chief_complaint = "כאבים בחזה מאז הבוקר"
        summary.findings = "רגישות בחזה"
        summary.treatment_plan = "הפניה לחדר מיון"
        summary.recommendations = "בדיקת טרופונין"
        summary.summary_text = "מטופל עם כאבי חזה"
        summary.notes = None

        # Step 4: Encrypt summary before save
        encrypt_summary_fields(summary)
        assert _is_encrypted(summary.chief_complaint)
        assert _is_encrypted(summary.summary_text)
        assert summary.notes is None  # None stays None

        # Step 5: Decrypt for display
        decrypt_summary_fields(summary)
        assert summary.chief_complaint == "כאבים בחזה מאז הבוקר"
        assert summary.treatment_plan == "הפניה לחדר מיון"

    def test_encrypted_text_sent_to_llm_is_garbage(self):
        """This is what caused INC-011: encrypted text → LLM → empty result."""
        transcription = MagicMock()
        transcription.full_text = "שיחה רפואית בעברית"
        encrypt_transcription_fields(transcription)

        # If we DON'T decrypt (the bug), LLM gets base64 gibberish
        raw_text = transcription.full_text
        assert " " not in raw_text[:40], "Encrypted text has no Hebrew spaces"
        assert len(raw_text) > 50, "Encrypted text is long base64"
        # LLM would return empty summary for this input


class TestMakeSessionIsolation:
    """Verify _make_session creates independent engine."""

    def test_make_session_returns_factory_and_engine(self):
        from app.tasks import _make_session
        SessionLocal, engine = _make_session()
        assert SessionLocal is not None
        assert engine is not None

    def test_two_sessions_are_independent(self):
        from app.tasks import _make_session
        s1, e1 = _make_session()
        s2, e2 = _make_session()
        assert e1 is not e2, "Each call should create a new engine (INC-009 fix)"
