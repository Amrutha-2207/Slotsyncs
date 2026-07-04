"""PDF export of the finalised timetable (VIT-AP Tue–Sat grid)."""
from __future__ import annotations
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
)

from .slots import (
    DAYS, DAY_NAMES, THEORY_GRID, LAB_GRID, THEORY_BANDS, LAB_BANDS,
    parse_slot_string,
)
from .timetable import build_color_map, SOFT_COLORS


def _fmt(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def _theory_padded(day: str) -> list[str | None]:
    c = THEORY_GRID[day]
    return [c[0], c[1], c[2], c[3], c[4], None,
            c[5], c[6], c[7], c[8], c[9], None]


def _theory_band_padded() -> list[tuple[int, int] | None]:
    b = THEORY_BANDS
    return [b[0], b[1], b[2], b[3], b[4], None,
            b[5], b[6], b[7], b[8], b[9], None]


def export_timetable_pdf(selected: list[dict], student_name: str = "") -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=10 * mm, rightMargin=10 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
        title="SlotSync Timetable",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("T", parent=styles["Title"], fontName="Helvetica-Bold",
                           fontSize=20, leading=24, textColor=colors.HexColor("#0F172A"))
    sub = ParagraphStyle("S", parent=styles["Normal"], fontName="Helvetica",
                         fontSize=9, textColor=colors.HexColor("#64748B"), spaceAfter=10)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                        fontSize=11, textColor=colors.HexColor("#0F172A"),
                        spaceBefore=10, spaceAfter=6)

    story: list = []
    story.append(Paragraph("SlotSync — Timetable", title))
    subtitle = "VIT-AP FFCS Planner"
    if student_name:
        subtitle = f"{student_name} · {subtitle}"
    story.append(Paragraph(subtitle, sub))

    color_map = build_color_map(selected)

    # -------- Timetable grid --------
    # Row 0: HR 1..12 header
    # Row 1: Theory times (padded)
    # Row 2: Lab times
    # Then, per day: Theory row + Lab row
    header = [""] + [f"HR {i}" for i in range(1, 13)]

    theory_time_row = ["Theory"]
    for band in _theory_band_padded():
        if band is None:
            theory_time_row.append("—")
        else:
            theory_time_row.append(f"{_fmt(band[0])}\n{_fmt(band[1])}")

    lab_time_row = ["Lab"]
    for s, e in LAB_BANDS:
        lab_time_row.append(f"{_fmt(s)}\n{_fmt(e)}")

    body: list[list] = [header, theory_time_row, lab_time_row]

    # Collect cells that should be coloured
    # style_ops[(row, col)] = (bg_hex, is_lab_bool)
    style_ops: dict[tuple[int, int], tuple[str, bool]] = {}

    for day in DAYS:
        # ---- Theory row ----
        theory_row = [f"{DAY_NAMES[day]}\n(Theory)"]
        r = len(body)
        for col_idx, cell in enumerate(_theory_padded(day), start=1):
            if cell is None:
                theory_row.append("")
                continue
            atoms = {tok.strip().upper() for tok in cell.split("/") if tok.strip()}
            owner = None
            matched = ""
            for c in selected:
                catoms = set(parse_slot_string(c.get("theory_slot", "")))
                hit = atoms & catoms
                if hit:
                    owner = c
                    matched = sorted(hit)[0]
                    break
            if owner:
                theory_row.append(f"{owner['course_code']}\n{owner.get('faculty_theory','') or owner.get('faculty','')}\n{matched}")
                style_ops[(r, col_idx)] = (color_map[owner["course_code"]], False)
            else:
                theory_row.append(cell)
        body.append(theory_row)

        # ---- Lab row ----
        lab_row = [f"{DAY_NAMES[day]}\n(Lab)"]
        r = len(body)
        for col_idx, atom in enumerate(LAB_GRID[day], start=1):
            atom_u = atom.upper()
            owner = None
            for c in selected:
                catoms = set(parse_slot_string(c.get("lab_slot", "")))
                if atom_u in catoms:
                    owner = c
                    break
            if owner:
                lab_row.append(f"{owner['course_code']}\n{owner.get('faculty_lab','') or owner.get('faculty','')}\n{atom_u}")
                style_ops[(r, col_idx)] = (color_map[owner["course_code"]], True)
            else:
                lab_row.append(atom_u)
        body.append(lab_row)

    # Column widths: label col wider, rest equal
    label_w = 26 * mm
    remaining = (297 - 20 - 26) * mm  # landscape A4 minus margins minus label col
    col_w = remaining / 12
    col_widths = [label_w] + [col_w] * 12

    table = Table(body, colWidths=col_widths, repeatRows=3)
    ts = TableStyle([
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 8),
        # Time rows
        ("BACKGROUND", (0, 1), (-1, 2), colors.HexColor("#F8FAFC")),
        ("TEXTCOLOR",  (0, 1), (-1, 2), colors.HexColor("#334155")),
        ("FONTSIZE",   (0, 1), (-1, 2), 6.5),
        ("FONTNAME",   (0, 1), (0, 2),  "Helvetica-Bold"),
        # Body
        ("FONTSIZE",   (0, 3), (-1, -1), 7),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        # Day label column
        ("BACKGROUND", (0, 3), (0, -1), colors.HexColor("#FAFAF7")),
        ("FONTNAME",   (0, 3), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",  (0, 3), (0, -1), colors.HexColor("#0F172A")),
        ("FONTSIZE",   (0, 3), (0, -1), 8),
    ])
    for (r, c), (hex_color, _) in style_ops.items():
        ts.add("BACKGROUND", (c, r), (c, r), colors.HexColor(hex_color))
        ts.add("FONTNAME", (c, r), (c, r), "Helvetica-Bold")
        ts.add("TEXTCOLOR", (c, r), (c, r), colors.HexColor("#0F172A"))
    table.setStyle(ts)
    story.append(table)

    # -------- Selected courses list --------
    story.append(Paragraph("Selected Courses", h2))
    header2 = ["Code", "Course", "Faculty", "Theory", "Lab", "Credits"]
    body2 = [header2]
    total = 0
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
            total += int(c.get("credits", 0))
        except Exception:
            pass
    body2.append(["", "", "", "", "Total", str(total)])

    t2 = Table(body2, colWidths=[22 * mm, 75 * mm, 65 * mm, 40 * mm, 40 * mm, 20 * mm])
    t2s = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2),
         [colors.HexColor("#FAFAF7"), colors.white]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F1F5F9")),
        ("FONTNAME",   (4, -1), (-1, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
    ])
    for i in range(1, len(body2) - 1):
        col = SOFT_COLORS[(i - 1) % len(SOFT_COLORS)]
        t2s.add("BACKGROUND", (0, i), (0, i), colors.HexColor(col))
    t2.setStyle(t2s)
    story.append(t2)

    doc.build(story)
    return buf.getvalue()
