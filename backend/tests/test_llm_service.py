"""Tests for LLM service logic (no API calls).

Covers: normalize_diagnosis, JSON parsing fallback.
"""
import pytest
from app.services.llm_service import normalize_diagnosis


class TestNormalizeDiagnosis:
    def test_list_of_dicts(self):
        raw = [
            {"code": "M54.5", "description": "כאב גב תחתון"},
            {"code": "I10", "description": "יתר לחץ דם"},
        ]
        result = normalize_diagnosis(raw)
        assert len(result) == 2
        assert result[0] == {"code": "M54.5", "description": "כאב גב תחתון"}

    def test_list_of_strings(self):
        raw = ["כאב ראש", "סחרחורת"]
        result = normalize_diagnosis(raw)
        assert len(result) == 2
        assert result[0] == {"code": "", "description": "כאב ראש"}

    def test_mixed_list(self):
        raw = [
            "כאב גב",
            {"code": "J06", "label": "זיהום דרכי נשימה עליונות"},
        ]
        result = normalize_diagnosis(raw)
        assert len(result) == 2
        assert result[0]["description"] == "כאב גב"
        assert result[1]["description"] == "זיהום דרכי נשימה עליונות"

    def test_dict_with_label_fallback(self):
        raw = [{"code": "E11", "label": "סוכרת סוג 2"}]
        result = normalize_diagnosis(raw)
        assert result[0]["description"] == "סוכרת סוג 2"

    def test_empty_list(self):
        assert normalize_diagnosis([]) == []

    def test_none(self):
        assert normalize_diagnosis(None) == []

    def test_not_a_list(self):
        assert normalize_diagnosis("כאב ראש") == []
        assert normalize_diagnosis(42) == []
        assert normalize_diagnosis({"code": "X"}) == []

    def test_missing_code_defaults_empty(self):
        raw = [{"description": "כאב"}]
        result = normalize_diagnosis(raw)
        assert result[0]["code"] == ""
