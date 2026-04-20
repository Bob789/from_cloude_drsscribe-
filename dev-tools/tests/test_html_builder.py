"""Unit tests for the dev-tools HTML builder (no browser required)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import _build_flat_html, _esc  # noqa: E402


def test_esc_handles_html_chars():
    assert _esc("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert _esc('a"b') == "a&quot;b"
    assert _esc("") == ""
    assert _esc(None) == ""  # type: ignore[arg-type]


def test_build_flat_html_uses_snapshot_html_as_is():
    snapshot = {
        "title": "Test",
        "url": "https://example.com/",
        "html": "<!doctype html><html><body><div>Hello</div></body></html>",
    }
    out = _build_flat_html(snapshot)
    assert "<!doctype html>" in out
    assert "Hello" in out


def test_build_flat_html_fallback_when_missing_html():
    snapshot = {
        "title": "Test",
        "url": "https://example.com/",
    }
    out = _build_flat_html(snapshot)
    assert "Flatten failed" in out
    assert "https://example.com/" in out


def test_build_flat_html_escapes_in_fallback():
    snapshot = {
        "title": "<script>alert(1)</script>",
        "url": "x\"><img src=x onerror=alert(1)>",
    }
    out = _build_flat_html(snapshot)
    assert "<script>alert(1)</script>" not in out
    assert "&lt;img" in out
