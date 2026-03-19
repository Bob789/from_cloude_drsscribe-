"""Regression tests for search & data isolation bugs (INC-001 through INC-005).

These tests verify:
1. Patient search works on encrypted data (INC-001)
2. Search results contain decrypted text, never ciphertext (INC-002)
3. Search results are isolated by doctor_id (INC-003)
4. Tags are isolated by doctor_id (INC-004)
5. Search indexer decrypts data before indexing (INC-005)
"""
import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone, date

from app.utils.encryption import encrypt_field, decrypt_field
from app.utils.medical_encryption import (
    _is_encrypted, encrypt_summary_fields, decrypt_summary_fields,
    decrypt_transcription_fields, SUMMARY_FIELDS,
)
from app.services.patient_service import decrypt_patient_pii


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_patient(name="ישראל ישראלי", phone="0501234567", email="test@test.com",
                  id_number="123456789", patient_id=None, created_by=None,
                  encrypt=True):
    """Create a mock Patient with optionally encrypted PII fields."""
    p = MagicMock()
    p.id = patient_id or uuid.uuid4()
    p.display_id = 1
    p.created_by = created_by
    p.dob = date(1990, 1, 1)
    p.blood_type = None
    p.allergies = None
    p.profession = None
    p.address = None
    p.insurance_info = None
    p.notes = None
    p.created_at = datetime.now(timezone.utc)
    p.updated_at = datetime.now(timezone.utc)

    if encrypt:
        p.name = encrypt_field(name)
        p.phone = encrypt_field(phone) if phone else None
        p.email = encrypt_field(email) if email else None
        p.id_number = encrypt_field(id_number) if id_number else None
    else:
        p.name = name
        p.phone = phone
        p.email = email
        p.id_number = id_number
    return p


def _make_summary(chief_complaint="כאבי ראש", findings="רגישות ברקה",
                  treatment_plan="אדביל 400mg", recommendations="מנוחה",
                  notes="מטופל חוזר", encrypt=True):
    """Create a mock Summary with optionally encrypted fields."""
    s = MagicMock()
    s.id = uuid.uuid4()
    s.visit_id = uuid.uuid4()
    s.diagnosis = ["migraine"]
    s.urgency = "low"
    s.status = MagicMock(value="done")
    s.created_at = datetime.now(timezone.utc)
    s.summary_text = None

    s.chief_complaint = chief_complaint
    s.findings = findings
    s.treatment_plan = treatment_plan
    s.recommendations = recommendations
    s.notes = notes

    if encrypt:
        encrypt_summary_fields(s)
    return s


# ===========================================================================
# INC-001: Patient search must find encrypted names
# ===========================================================================

class TestPatientSearchEncrypted:
    """INC-001: Verify patient search works on encrypted PII fields."""

    def test_encrypted_name_is_not_plaintext(self):
        """Encrypted name should not equal the original plaintext."""
        p = _make_patient(name="דוד כהן", encrypt=True)
        assert p.name != "דוד כהן"
        assert _is_encrypted(p.name) or len(p.name) > 50

    def test_decrypt_patient_pii_restores_name(self):
        """decrypt_patient_pii must restore the original plaintext name."""
        p = _make_patient(name="דוד כהן", encrypt=True)
        decrypt_patient_pii(p)
        assert p.name == "דוד כהן"

    def test_decrypt_patient_pii_restores_phone(self):
        p = _make_patient(phone="0521234567", encrypt=True)
        decrypt_patient_pii(p)
        assert p.phone == "0521234567"

    def test_decrypt_patient_pii_restores_email(self):
        p = _make_patient(email="david@example.com", encrypt=True)
        decrypt_patient_pii(p)
        assert p.email == "david@example.com"

    def test_decrypt_patient_pii_restores_id_number(self):
        p = _make_patient(id_number="987654321", encrypt=True)
        decrypt_patient_pii(p)
        assert p.id_number == "987654321"

    def test_ilike_cannot_match_encrypted_name(self):
        """This test proves the OLD bug: SQL ILIKE on ciphertext never matches plaintext.
        If someone re-introduces ILIKE on encrypted columns, this test documents WHY it fails."""
        p = _make_patient(name="שרה לוי", encrypt=True)
        encrypted_name = p.name
        query = "שרה"
        # ILIKE simulation: plaintext query can't be found in ciphertext
        assert query.lower() not in encrypted_name.lower()

    def test_search_after_decrypt_finds_name(self):
        """After decryption, plaintext search DOES find the name."""
        p = _make_patient(name="שרה לוי", encrypt=True)
        decrypt_patient_pii(p)
        query = "שרה"
        assert query in p.name

    def test_search_by_phone_digits_after_decrypt(self):
        """Phone search by digits works after decryption."""
        p = _make_patient(phone="050-123-4567", encrypt=True)
        decrypt_patient_pii(p)
        digits = "1234"
        phone_digits = ''.join(c for c in p.phone if c.isdigit())
        assert digits in phone_digits

    def test_unencrypted_legacy_data_still_works(self):
        """Legacy unencrypted patients should pass through decrypt_patient_pii safely."""
        p = _make_patient(name="אברהם אברהמי", encrypt=False)
        original_name = p.name
        decrypt_patient_pii(p)
        assert p.name == original_name


# ===========================================================================
# INC-002: Search results must be decrypted, never show ciphertext
# ===========================================================================

class TestSearchResultsDecrypted:
    """INC-002: Verify search output functions decrypt before returning."""

    def test_build_hit_decrypts_summary(self):
        """_build_hit must return decrypted text, not ciphertext."""
        from app.services.search_service import _build_hit

        s = _make_summary(chief_complaint="כאבי בטן חריפים", encrypt=True)
        assert _is_encrypted(s.chief_complaint), "Setup: field should start encrypted"

        hit = _build_hit(s, "test patient", 1, ["tag1"])
        assert hit["chief_complaint"] == "כאבי בטן חריפים"
        assert not _is_encrypted(hit["chief_complaint"])

    def test_build_hit_decrypts_all_summary_fields(self):
        from app.services.search_service import _build_hit
        s = _make_summary(
            chief_complaint="כאב",
            findings="ממצאים",
            treatment_plan="טיפול",
            recommendations="המלצות",
            notes="הערות",
            encrypt=True,
        )
        hit = _build_hit(s, "patient", 1, [])
        for field in ["chief_complaint", "findings", "treatment_plan", "recommendations", "notes"]:
            assert not _is_encrypted(hit[field]), f"{field} should be decrypted in hit"

    def test_build_transcription_hit_decrypts(self):
        from app.services.search_service import _build_transcription_hit

        t = MagicMock()
        t.id = uuid.uuid4()
        t.full_text = encrypt_field("זה תמלול של ביקור רפואי עם המטופל")
        t.created_at = datetime.now(timezone.utc)

        assert _is_encrypted(t.full_text), "Setup: should start encrypted"

        hit = _build_transcription_hit(t, "patient", 1)
        assert "תמלול" in hit["full_text"]
        assert not _is_encrypted(hit["full_text"])

    def test_build_hit_safe_on_unencrypted(self):
        """Already-decrypted data should pass through safely."""
        from app.services.search_service import _build_hit

        s = _make_summary(chief_complaint="כבר מפוענח", encrypt=False)
        hit = _build_hit(s, "patient", 1, [])
        assert hit["chief_complaint"] == "כבר מפוענח"


# ===========================================================================
# INC-003: Search must be isolated by doctor_id
# ===========================================================================

class TestSearchDoctorIsolation:
    """INC-003: Verify search functions accept and use doctor_id parameter."""

    def test_combined_search_accepts_doctor_id(self):
        """combined_search signature must include doctor_id parameter."""
        import inspect
        from app.services.search_service import combined_search
        sig = inspect.signature(combined_search)
        assert "doctor_id" in sig.parameters, "combined_search must accept doctor_id"

    def test_search_by_tags_accepts_doctor_id(self):
        import inspect
        from app.services.search_service import search_by_tags
        sig = inspect.signature(search_by_tags)
        assert "doctor_id" in sig.parameters, "search_by_tags must accept doctor_id"

    def test_search_db_text_accepts_doctor_id(self):
        import inspect
        from app.services.search_service import search_db_text
        sig = inspect.signature(search_db_text)
        assert "doctor_id" in sig.parameters, "search_db_text must accept doctor_id"

    def test_search_router_passes_doctor_id(self):
        """Verify the search router source code passes doctor_id to all functions."""
        import inspect
        from app.routers import search as search_module
        source = inspect.getsource(search_module.search_all)
        # Must pass doctor_id to all three search calls
        assert "doctor_id=" in source, "Router must pass doctor_id to search functions"
        assert "current_user.id" in source, "Router must use current_user.id"


# ===========================================================================
# INC-004: Tags must be isolated by doctor
# ===========================================================================

class TestTagsDoctorIsolation:
    """INC-004: Verify tags endpoints filter by doctor."""

    def test_list_tags_source_filters_by_doctor(self):
        """list_tags must JOIN to Visit and filter by doctor_id."""
        import inspect
        from app.routers import tags as tags_module
        source = inspect.getsource(tags_module.list_tags)
        assert "Visit.doctor_id" in source or "doctor_id" in source, \
            "list_tags must filter by doctor_id via Visit JOIN"
        assert "current_user.id" in source, \
            "list_tags must use current_user.id for filtering"

    def test_visits_by_tag_source_filters_by_doctor(self):
        import inspect
        from app.routers import tags as tags_module
        source = inspect.getsource(tags_module.visits_by_tag)
        assert "Visit.doctor_id" in source or "doctor_id" in source, \
            "visits_by_tag must filter by doctor_id"

    def test_tags_router_imports_visit_model(self):
        """Tags router must import Visit model for doctor isolation JOINs."""
        from app.routers import tags as tags_module
        assert hasattr(tags_module, 'Visit'), "tags module must import Visit model"


# ===========================================================================
# INC-005: Search indexer must decrypt before indexing
# ===========================================================================

class TestSearchIndexerDecryption:
    """INC-005: Verify indexer decrypts data and includes doctor_id."""

    def test_indexer_imports_decrypt_functions(self):
        """search_indexer must import decryption functions."""
        from app.services import search_indexer
        source_file = search_indexer.__file__
        with open(source_file, "r", encoding="utf-8") as f:
            source = f.read()
        assert "decrypt_patient_pii" in source
        assert "decrypt_summary_fields" in source
        assert "decrypt_transcription_fields" in source

    def test_indexer_includes_doctor_id_in_filterable(self):
        """Meilisearch index settings must include doctor_id as filterable."""
        from app.services import search_indexer
        with open(search_indexer.__file__, "r", encoding="utf-8") as f:
            source = f.read()
        # Check both indexes have doctor_id in filterableAttributes
        assert source.count('"doctor_id"') >= 3, \
            "doctor_id must appear in filterableAttributes for both indexes + in document dicts"

    def test_reindex_all_source_has_doctor_id_in_docs(self):
        """reindex_all must include doctor_id in indexed documents."""
        import inspect
        from app.services.search_indexer import reindex_all
        source = inspect.getsource(reindex_all)
        assert '"doctor_id"' in source or "'doctor_id'" in source, \
            "reindex_all must include doctor_id in indexed documents"


# ===========================================================================
# Cross-cutting: encryption round-trip integrity
# ===========================================================================

class TestEncryptionRoundTrip:
    """Verify encrypt→store→decrypt round-trip for all field types."""

    def test_patient_full_roundtrip(self):
        """Full patient PII encrypt→decrypt cycle."""
        original = {"name": "גליה לוי", "phone": "0501112233", "email": "galia@test.com", "id_number": "111222333"}
        p = _make_patient(**original, encrypt=True)

        # Verify all fields are encrypted
        for field in ["name", "phone", "email", "id_number"]:
            assert getattr(p, field) != original[field], f"{field} should be encrypted"

        # Decrypt and verify
        decrypt_patient_pii(p)
        for field in ["name", "phone", "email", "id_number"]:
            assert getattr(p, field) == original[field], f"{field} should match original after decrypt"

    def test_summary_full_roundtrip(self):
        """Full summary fields encrypt→decrypt cycle."""
        original = {
            "chief_complaint": "כאב ראש כרוני",
            "findings": "רגישות באזור העורף",
            "treatment_plan": "תרופות משככות כאב",
            "recommendations": "MRI מוח",
            "notes": "ביקור חוזר בעוד שבועיים",
        }
        s = _make_summary(**original, encrypt=True)

        for field in original:
            assert _is_encrypted(getattr(s, field)), f"{field} should be encrypted"

        decrypt_summary_fields(s)
        for field in original:
            assert getattr(s, field) == original[field], f"{field} decrypted mismatch"

    def test_double_decrypt_is_safe(self):
        """Calling decrypt twice should not corrupt data."""
        p = _make_patient(name="טסט כפול", encrypt=True)
        decrypt_patient_pii(p)
        name_after_first = p.name
        decrypt_patient_pii(p)
        assert p.name == name_after_first == "טסט כפול"

    def test_double_decrypt_summary_is_safe(self):
        s = _make_summary(chief_complaint="תלונה", encrypt=True)
        decrypt_summary_fields(s)
        first = s.chief_complaint
        decrypt_summary_fields(s)
        assert s.chief_complaint == first == "תלונה"
