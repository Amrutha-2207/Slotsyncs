"""PDF export of the finalised timetable."""
from __future__ import annotations
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

from .timetable import build_timetable_grid, DAY_NAMES
from .slots import DAYS, band_label

_PALETTE = [
    "#DBEAFE", "#DCFCE7", "#FEF3C7", "#FCE7F3", "#EDE9FE",
    "#FFE4E6", "#CFFAFE", "#FEF9C3", "#E0F2FE", "#F3E8FF",
]


def export_timetable_pdf(selected: list[dict], student_name: str = "") -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=14 * mm, rightMargin=14 * mm,
        topMargin=14 * mm, bottomMargin=14 * mm,
        title="SlotSync Timetable",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "T", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=22, leading=26, textColor=colors.HexColor("#0F172A"),
        spaceAfter=2,
    )
    sub_style = ParagraphStyle(
        "S", parent=styles["Normal"], fontName="Helvetica",
        fontSize=10, textColor=colors.HexColor("#64748B"), spaceAfter=12,
    )
    h2 = ParagraphStyle(
        "H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=12, textColor=colors.HexColor("#0F172A"),
        spaceBefore=10, spaceAfter=6,
    )

    story: list = []
    story.append(Paragraph("SlotSync — Timetable", title_style))
    subtitle = "VIT-AP FFCS Planner"
    if student_name:
        subtitle = f"{student_name} · {subtitle}"
    story.append(Paragraph(subtitle, sub_style))

    grid, color_map = build_timetable_grid(selected)

    # ---------------- Timetable Table ----------------
    header = ["Time"] + [DAY_NAMES[d] for d in DAYS]
    body = [header]
    for row_label, row in grid.iterrows():
        line = [row_label]
        for col in grid.columns:
            v = row[col]
            if not v:
                line.append("")
            else:
                code, fac, slot, comp = v.split("|", 3)
                line.append(f"{code}\n{fac}\n{slot}")
        body.append(line)

    col_widths = [28 * mm] + [45 * mm] * 5
    table = Table(body, colWidths=col_widths, repeatRows=1)

    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TEXTCOLOR", (0, 1), (0, -1), colors.HexColor("#64748B")),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS", (1, 1), (0, -1),
         [colors.HexColor("#FAFAF7"), colors.white]),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
    ])

    # Colour occupied cells to match the on-screen palette.
    for r_idx, (row_label, row) in enumerate(grid.iterrows(), start=1):
        for c_idx, col in enumerate(grid.columns, start=1):
            v = row[col]
            if v:
                code = v.split("|", 1)[0]
                hex_color = color_map.get(code, "#F3F4F6")
                ts.add("BACKGROUND", (c_idx, r_idx), (c_idx, r_idx),
                       colors.HexColor(hex_color))
                ts.add("FONTNAME", (c_idx, r_idx), (c_idx, r_idx), "Helvetica-Bold")
                ts.add("TEXTCOLOR", (c_idx, r_idx), (c_idx, r_idx),
                       colors.HexColor("#0F172A"))
    table.setStyle(ts)
    story.append(table)

    # ---------------- Selected Courses List ----------------
    story.append(Paragraph("Selected Courses", h2))
    header2 = ["Code", "Course", "Faculty", "Theory", "Lab", "Credits"]
    body2 = [header2]
    total_credits = 0
    for i, c in enumerate(selected):
        body2.append([
            c.get("course_code", ""),
            c.get("course_name", ""),
            c.get("faculty", ""),
            c.get("theory_slot", "") or "—",
            c.get("lab_slot", "") or "—",
            str(c.get("credits", 0)),
        ])
        try:
            total_credits += int(c.get("credits", 0))
        except Exception:
            pass
    body2.append(["", "", "", "", "Total", str(total_credits)])

    t2 = Table(body2, colWidths=[22 * mm, 75 * mm, 60 * mm, 30 * mm, 30 * mm, 20 * mm])
    t2s = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2),
         [colors.HexColor("#FAFAF7"), colors.white]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F1F5F9")),
        ("FONTNAME", (4, -1), (-1, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ])
    for i, c in enumerate(selected, start=1):
        hex_color = _PALETTE[(i - 1) % len(_PALETTE)]
        t2s.add("BACKGROUND", (0, i), (0, i), colors.HexColor(hex_color))
    t2.setStyle(t2s)
    story.append(t2)

    doc.build(story)
    return buf.getvalue()
