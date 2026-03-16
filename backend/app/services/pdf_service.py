import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Hebrew-compatible font
_FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "fonts")
_font_registered = False


def _register_fonts():
    global _font_registered
    if _font_registered:
        return
    regular = os.path.join(_FONT_DIR, "Heebo-Regular.ttf")
    bold = os.path.join(_FONT_DIR, "Heebo-Bold.ttf")
    if os.path.exists(regular):
        pdfmetrics.registerFont(TTFont("Heebo", regular))
    if os.path.exists(bold):
        pdfmetrics.registerFont(TTFont("Heebo-Bold", bold))
    _font_registered = True


def _reverse_hebrew(text: str) -> str:
    """ReportLab doesn't handle RTL. Reverse Hebrew runs for correct display."""
    if not text:
        return ""
    # Process line by line
    lines = text.split("\n")
    result = []
    for line in lines:
        # Split into runs of Hebrew and non-Hebrew
        segments = []
        current = []
        is_hebrew = False
        for ch in line:
            ch_is_heb = '\u0590' <= ch <= '\u05FF' or '\uFB1D' <= ch <= '\uFB4F'
            if current and ch_is_heb != is_hebrew:
                segments.append((''.join(current), is_hebrew))
                current = []
            current.append(ch)
            is_hebrew = ch_is_heb
        if current:
            segments.append((''.join(current), is_hebrew))
        # Reverse Hebrew segments and reverse order for RTL
        reversed_segs = []
        for text_seg, is_heb in reversed(segments):
            if is_heb:
                reversed_segs.append(text_seg[::-1])
            else:
                reversed_segs.append(text_seg)
        result.append(''.join(reversed_segs))
    return '\n'.join(result)


def _format_datetime(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y  %H:%M")
    except Exception:
        return iso_str[:10] if len(iso_str) >= 10 else iso_str


def generate_summary_pdf(summary: dict, patient: dict = None, visit: dict = None) -> bytes:
    _register_fonts()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=40, bottomMargin=50)

    font_name = "Heebo" if _font_registered else "Helvetica"
    font_bold = "Heebo-Bold" if _font_registered else "Helvetica-Bold"

    styles = getSampleStyleSheet()
    rtl_style = ParagraphStyle("RTL", parent=styles["Normal"], fontName=font_name, alignment=TA_RIGHT, fontSize=11, leading=18)
    title_style = ParagraphStyle("TitleRTL", parent=styles["Title"], fontName=font_bold, alignment=TA_CENTER, fontSize=20, spaceAfter=4)
    subtitle_style = ParagraphStyle("SubtitleRTL", parent=styles["Normal"], fontName=font_name, alignment=TA_CENTER, fontSize=10, textColor=colors.grey)
    heading_style = ParagraphStyle("HeadingRTL", parent=styles["Heading2"], fontName=font_bold, alignment=TA_RIGHT, fontSize=13, textColor=colors.HexColor("#1a56db"), spaceBefore=14, spaceAfter=4)
    table_font = font_name

    elements = []

    # Header
    elements.append(Paragraph("Doctor Scribe AI", title_style))
    elements.append(Paragraph(_reverse_hebrew("סיכום ביקור רפואי"), subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#38bdf8")))
    elements.append(Spacer(1, 14))

    # Patient info table
    if patient:
        start_time = visit.get("start_time", "") if visit else ""
        formatted_time = _format_datetime(start_time) if start_time else ""

        doctor_name = visit.get("doctor_name", "") if visit else ""
        patient_rows = [
            [_reverse_hebrew(patient.get("name", "")), _reverse_hebrew("שם מטופל")],
            [patient.get("id_number", "—"), _reverse_hebrew("ת.ז.")],
            [formatted_time, _reverse_hebrew("תאריך ושעה")],
        ]
        if doctor_name:
            patient_rows.append([_reverse_hebrew(doctor_name), _reverse_hebrew("רופא מטפל")])

        table = Table(patient_rows, colWidths=[280, 120])
        table.setStyle(TableStyle([
            ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#e0f2fe")),
            ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#1e3a5f")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -1), table_font),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 18))

    # Summary sections
    sections = [
        ("תלונה עיקרית", summary.get("chief_complaint", "")),
        ("ממצאים", summary.get("findings", "")),
        ("תכנית טיפול", summary.get("treatment_plan", "")),
        ("המלצות", summary.get("recommendations", "")),
    ]
    for title, content in sections:
        if content:
            elements.append(Paragraph(_reverse_hebrew(title), heading_style))
            # Handle multiline content
            for line in content.split("\n"):
                if line.strip():
                    elements.append(Paragraph(_reverse_hebrew(line), rtl_style))
            elements.append(Spacer(1, 6))

    # Diagnoses
    diagnoses = summary.get("diagnosis", [])
    if diagnoses:
        elements.append(Paragraph(_reverse_hebrew("אבחנות"), heading_style))
        diag_rows = [[_reverse_hebrew("תיאור"), _reverse_hebrew("קוד")]]
        for diag in diagnoses:
            if isinstance(diag, dict):
                desc = diag.get("description", diag.get("label", ""))
                diag_rows.append([_reverse_hebrew(desc), diag.get("code", "")])
        if len(diag_rows) > 1:
            diag_table = Table(diag_rows, colWidths=[320, 80])
            diag_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, -1), table_font),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(diag_table)

    # Signature
    elements.append(Spacer(1, 40))
    elements.append(HRFlowable(width="40%", thickness=0.5, color=colors.grey, hAlign="RIGHT"))
    elements.append(Paragraph(_reverse_hebrew("חתימת רופא"), ParagraphStyle("Sig", parent=rtl_style, fontSize=10, textColor=colors.grey)))

    # Print date footer
    elements.append(Spacer(1, 20))
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"{now} :{_reverse_hebrew('הודפס')}", ParagraphStyle("Footer", parent=rtl_style, fontSize=8, textColor=colors.lightgrey)))

    doc.build(elements)
    return buffer.getvalue()
