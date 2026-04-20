"""Unit tests for the dev-tools HTML builder (no browser required)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import _build_flat_html, _esc, _style_to_css  # noqa: E402


def test_esc_handles_html_chars():
    assert _esc("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert _esc('a"b') == "a&quot;b"
    assert _esc("") == ""
    assert _esc(None) == ""  # type: ignore[arg-type]


def test_style_to_css_concatenates():
    css = _style_to_css({"color": "red", "font-size": "14px"})
    assert "color:red" in css
    assert "font-size:14px" in css
    assert ";" in css


def test_build_flat_html_basic_structure():
    snapshot = {
        "docW": 800,
        "docH": 600,
        "title": "Test",
        "url": "https://example.com/",
        "elements": [
            {
                "tag": "div",
                "x": 10, "y": 20, "w": 100, "h": 30,
                "text": "Hello",
                "ariaLabel": "",
                "role": "",
                "imgSrc": None,
                "style": {"color": "#fff", "background-color": "#000"},
            },
        ],
    }
    out = _build_flat_html(snapshot, b"\x89PNG\r\n\x1a\n")
    assert "<!doctype html>" in out
    assert "Hello" in out
    assert "left:10px" in out
    assert "top:20px" in out
    assert "width:100px" in out
    assert 'data:image/png;base64,' in out
    assert "https://example.com/" in out


def test_build_flat_html_escapes_text():
    snapshot = {
        "docW": 100, "docH": 100, "title": "x", "url": "x",
        "elements": [
            {"tag": "div", "x": 0, "y": 0, "w": 10, "h": 10,
             "text": "<img src=x onerror=alert(1)>",
             "ariaLabel": "", "role": "", "imgSrc": None, "style": {}}
        ],
    }
    out = _build_flat_html(snapshot, b"")
    assert "<img src=x" not in out
    assert "&lt;img" in out


def test_build_flat_html_skips_offscreen():
    snapshot = {
        "docW": 200, "docH": 200, "title": "x", "url": "x",
        "elements": [
            {"tag": "div", "x": -500, "y": -500, "w": 10, "h": 10,
             "text": "OFFSCREEN", "ariaLabel": "", "role": "",
             "imgSrc": None, "style": {}}
        ],
    }
    out = _build_flat_html(snapshot, b"")
    assert "OFFSCREEN" not in out
