"""Tests for medical field encryption/decryption.

Covers: encrypt_field, decrypt_field, _is_encrypted heuristic,
encrypt/decrypt_summary_fields, encrypt/decrypt_transcription_fields.
"""
import pytest
from unittest.mock import MagicMock
from app.utils.encryption import encrypt_field, decrypt_field
from app.utils.medical_encryption import (
    _is_encrypted, encrypt_summary_fields, decrypt_summary_fields,
    encrypt_transcription_fields, decrypt_transcription_fields,
    SUMMARY_FIELDS, TRANSCRIPTION_FIELDS,
)


class TestEncryptDecryptField:
    def test_roundtrip_hebrew(self):
        original = "כאבים חזקים בחזה מאז הבוקר"
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        assert decrypted == original

    def test_roundtrip_long_text(self):
        original = "תמלול ארוך " * 100
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        assert decrypted == original

    def test_empty_string_passthrough(self):
        assert encrypt_field("") == ""
        assert decrypt_field("") == ""

    def test_none_passthrough(self):
        assert encrypt_field(None) is None
        assert decrypt_field(None) is None

    def test_encrypted_differs_from_original(self):
        original = "מידע רפואי רגיש"
        encrypted = encrypt_field(original)
        assert encrypted != original
        assert len(encrypted) > len(original)

    def test_each_encryption_unique(self):
        """Different nonces should produce different ciphertext."""
        original = "test data"
        enc1 = encrypt_field(original)
        enc2 = encrypt_field(original)
        assert enc1 != enc2  # random nonce
        assert decrypt_field(enc1) == decrypt_field(enc2) == original


class TestIsEncrypted:
    def test_encrypted_value_detected(self):
        encrypted = encrypt_field("test value for detection")
        assert _is_encrypted(encrypted) is True

    def test_plaintext_not_detected(self):
        assert _is_encrypted("כאבים בחזה") is False
        assert _is_encrypted("short") is False

    def test_none_not_detected(self):
        assert _is_encrypted(None) is False

    def test_empty_not_detected(self):
        assert _is_encrypted("") is False


class TestSummaryFieldsEncryption:
    def _make_summary(self, **kwargs):
        mock = MagicMock()
        for field in SUMMARY_FIELDS:
            setattr(mock, field, kwargs.get(field, None))
        return mock

    def test_encrypt_decrypt_roundtrip(self):
        summary = self._make_summary(
            chief_complaint="כאבי ראש חזקים",
            findings="רגישות באזור הרקה",
            treatment_plan="אדביל 400mg",
            recommendations="מנוחה יומיים",
            summary_text="ביקור שגרתי",
            notes="מטופל חוזר",
        )

        encrypt_summary_fields(summary)

        # All fields should be encrypted (long base64)
        for field in SUMMARY_FIELDS:
            val = getattr(summary, field)
            assert _is_encrypted(val), f"{field} should be encrypted"

        decrypt_summary_fields(summary)

        assert summary.chief_complaint == "כאבי ראש חזקים"
        assert summary.findings == "רגישות באזור הרקה"
        assert summary.treatment_plan == "אדביל 400mg"
        assert summary.recommendations == "מנוחה יומיים"
        assert summary.summary_text == "ביקור שגרתי"
        assert summary.notes == "מטופל חוזר"

    def test_skip_none_fields(self):
        summary = self._make_summary(chief_complaint="כאב", findings=None)
        encrypt_summary_fields(summary)
        assert summary.findings is None  # not touched
        assert _is_encrypted(summary.chief_complaint)

    def test_skip_already_encrypted(self):
        summary = self._make_summary(chief_complaint="כאב")
        encrypt_summary_fields(summary)
        first_encryption = summary.chief_complaint
        encrypt_summary_fields(summary)  # second time
        assert summary.chief_complaint == first_encryption  # not double-encrypted


class TestTranscriptionFieldsEncryption:
    def _make_transcription(self, full_text=None):
        mock = MagicMock()
        mock.full_text = full_text
        return mock

    def test_roundtrip(self):
        t = self._make_transcription("רופא שלום מה מביא אותך היום? מטופל כאבים בגב")
        encrypt_transcription_fields(t)
        assert _is_encrypted(t.full_text)
        decrypt_transcription_fields(t)
        assert t.full_text == "רופא שלום מה מביא אותך היום? מטופל כאבים בגב"

    def test_skip_none(self):
        t = self._make_transcription(None)
        encrypt_transcription_fields(t)
        assert t.full_text is None
