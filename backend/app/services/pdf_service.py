import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_summary_pdf(summary: dict, patient: dict = None, visit: dict = None) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()
    rtl_style = ParagraphStyle("RTL", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=12, leading=16)
    title_style = ParagraphStyle("TitleRTL", parent=styles["Title"], alignment=TA_RIGHT, fontSize=18)
    heading_style = ParagraphStyle("HeadingRTL", parent=styles["Heading2"], alignment=TA_RIGHT, fontSize=14)

    elements = []

    elements.append(Paragraph("MedScribe AI - סיכום ביקור", title_style))
    elements.append(Spacer(1, 20))

    if patient:
        patient_data = [
            ["שם מטופל", patient.get("name", "")],
            ["ת.ז.", patient.get("id_number", "")],
            ["תאריך ביקור", visit.get("start_time", "")[:10] if visit else ""],
        ]
        table = Table(patient_data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.lightblue),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

    sections = [
        ("תלונה עיקרית", summary.get("chief_complaint", "")),
        ("ממצאים", summary.get("findings", "")),
        ("תכנית טיפול", summary.get("treatment_plan", "")),
        ("המלצות", summary.get("recommendations", "")),
    ]
    for title, content in sections:
        if content:
            elements.append(Paragraph(title, heading_style))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(content, rtl_style))
            elements.append(Spacer(1, 12))

    diagnoses = summary.get("diagnosis", [])
    if diagnoses:
        elements.append(Paragraph("אבחנות", heading_style))
        elements.append(Spacer(1, 6))
        for diag in diagnoses:
            if isinstance(diag, dict):
                elements.append(Paragraph(f"{diag.get('code', '')} - {diag.get('description', '')}", rtl_style))

    elements.append(Spacer(1, 40))
    elements.append(Paragraph("_________________________", rtl_style))
    elements.append(Paragraph("חתימת רופא", rtl_style))

    doc.build(elements)
    return buffer.getvalue()
