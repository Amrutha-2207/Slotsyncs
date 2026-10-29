"""Build a display-ready timetable from selected offerings.

Layout matches the official VIT-AP grid: 5 days × (Theory row + Lab row).
Theory has 10 cells; Lab has 12. We render them aligned as 12 columns with
theory columns 6 and 12 left empty (they fall inside the lab-only bands).
"""
from __future__ import annotations
from .slots import (
    DAYS, DAY_NAMES, THEORY_GRID, LAB_GRID, THEORY_BANDS, LAB_BANDS,
    theory_band_label, lab_band_label, parse_slot_string,
)


# Soft, non-harsh palette (Apple/Linear inspired).
SOFT_COLORS = [
    "#DBEAFE", "#DCFCE7", "#FEF3C7", "#FCE7F3", "#EDE9FE",
    "#FFE4E6", "#CFFAFE", "#FEF9C3", "#E0F2FE", "#F3E8FF",
    "#DCFCE7", "#FFEDD5",
]


# Theory-row layout padded to 12 columns (col 6 and 12 are lab-only bands).
def _theory_row_padded(day: str) -> list[str | None]:
    cells = THEORY_GRID[day]
    return [
        cells[0], cells[1], cells[2], cells[3], cells[4],
        None,                            # lab-only gap (12:30–13:10)
        cells[5], cells[6], cells[7], cells[8], cells[9],
        None,                            # lab-only tail (18:30–19:10)
    ]


def _theory_band_padded() -> list[tuple[int, int] | None]:
    return [
        THEORY_BANDS[0], THEORY_BANDS[1], THEORY_BANDS[2],
        THEORY_BANDS[3], THEORY_BANDS[4],
        None,
        THEORY_BANDS[5], THEORY_BANDS[6], THEORY_BANDS[7],
        THEORY_BANDS[8], THEORY_BANDS[9],
        None,
    ]


def _cell_atoms(cell: str | None) -> set[str]:
    if not cell:
        return set()
    return {tok.strip().upper() for tok in cell.split("/") if tok.strip()}


def _course_atoms(course: dict, kind: str) -> set[str]:
    slot_str = course.get("theory_slot" if kind == "theory" else "lab_slot") or ""
    return set(parse_slot_string(slot_str))


def build_color_map(selected: list[dict]) -> dict[str, str]:
    return {
        c.get("course_code", f"C{i}"): SOFT_COLORS[i % len(SOFT_COLORS)]
        for i, c in enumerate(selected)
    }


def grid_to_html(selected: list[dict]) -> str:
    """Render the whole timetable as self-contained HTML."""
    color_map = build_color_map(selected)

    # Column header (12 lab-based columns + a leading label column)
    hour_headers = "".join(
        f'<th class="tt-th">HR {i}</th>' for i in range(1, 13)
    )

    # Sub-header: theory bands
    theory_bands_sub = ""
    for band in _theory_band_padded():
        if band is None:
            theory_bands_sub += '<th class="tt-th-sub tt-sub-empty">—</th>'
        else:
            s, e = band
            theory_bands_sub += (
                f'<th class="tt-th-sub">{_fmt(s)}<br/>{_fmt(e)}</th>'
            )

    # Sub-header: lab bands
    lab_bands_sub = ""
    for s, e in LAB_BANDS:
        lab_bands_sub += (
            f'<th class="tt-th-sub">{_fmt(s)}<br/>{_fmt(e)}</th>'
        )

    body_rows: list[str] = []
    for day in DAYS:
        theory_cells = _render_theory_row(day, selected, color_map)
        lab_cells = _render_lab_row(day, selected, color_map)
        body_rows.append(
            f'<tr class="tt-day-head"><td rowspan="2" class="tt-day">'
            f'<div class="tt-day-name">{DAY_NAMES[day]}</div>'
            f'<div class="tt-day-lane">THEORY</div></td>'
            f'{theory_cells}</tr>'
            f'<tr class="tt-day-lab-row"><td class="tt-day tt-day-lab">'
            f'<div class="tt-day-lane">LAB</div></td>'
            f'{lab_cells}</tr>'
        )

    return (
        '<div class="tt-wrap"><table class="tt"><thead>'
        f'<tr><th class="tt-th tt-th-day" rowspan="3">Day</th>{hour_headers}</tr>'
        f'<tr class="tt-sub-row">{theory_bands_sub}</tr>'
        f'<tr class="tt-sub-row">{lab_bands_sub}</tr>'
        '</thead><tbody>'
        f'{"".join(body_rows)}'
        '</tbody></table></div>'
    )


def _fmt(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def _render_theory_row(day: str, selected: list[dict], color_map: dict[str, str]) -> str:
    padded = _theory_row_padded(day)
    out: list[str] = []
    for cell in padded:
        if cell is None:
            out.append('<td class="tt-cell tt-cell-empty tt-cell-gap"></td>')
            continue
        atoms = _cell_atoms(cell)
        # Which course (if any) occupies this cell via a matching atom?
        owner = None
        matched_atom = ""
        for c in selected:
            course_atoms = _course_atoms(c, "theory")
            hit = atoms & course_atoms
            if hit:
                owner = c
                matched_atom = sorted(hit)[0]
                break
        if owner:
            color = color_map.get(owner["course_code"], "#F3F4F6")
            out.append(
                f'<td class="tt-cell tt-filled" style="background:{color};">'
                f'<div class="tt-code">{owner["course_code"]}</div>'
                f'<div class="tt-fac">{owner.get("faculty_theory") or owner.get("faculty","")}</div>'
                f'<div class="tt-slot"><span class="tt-tag">T</span>{matched_atom}</div>'
                f'</td>'
            )
        else:
            out.append(
                f'<td class="tt-cell tt-cell-empty">'
                f'<span class="tt-cell-hint">{cell}</span></td>'
            )
    return "".join(out)


def _render_lab_row(day: str, selected: list[dict], color_map: dict[str, str]) -> str:
    cells = LAB_GRID[day]
    out: list[str] = []
    for atom in cells:
        atom_u = atom.upper()
        owner = None
        for c in selected:
            if atom_u in _course_atoms(c, "lab"):
                owner = c
                break
        if owner:
            color = color_map.get(owner["course_code"], "#F3F4F6")
            out.append(
                f'<td class="tt-cell tt-filled" style="background:{color};">'
                f'<div class="tt-code">{owner["course_code"]}</div>'
                f'<div class="tt-fac">{owner.get("faculty_lab") or owner.get("faculty","")}</div>'
                f'<div class="tt-slot"><span class="tt-tag tt-tag-lab">L</span>{atom_u}</div>'
                f'</td>'
            )
        else:
            out.append(
                f'<td class="tt-cell tt-cell-empty">'
                f'<span class="tt-cell-hint">{atom_u}</span></td>'
            )
    return "".join(out)
