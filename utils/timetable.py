"""Build a display-ready timetable DataFrame from selected offerings."""
from __future__ import annotations
import pandas as pd
from .slots import DAYS, TIME_BANDS, THEORY_GRID, LAB_GRID, band_label
from .clash import cells_of_course

# A soft, non-harsh palette (Apple/Linear inspired).
SOFT_COLORS = [
    "#DBEAFE",  # sky
    "#DCFCE7",  # mint
    "#FEF3C7",  # butter
    "#FCE7F3",  # blush
    "#EDE9FE",  # lavender
    "#FFE4E6",  # coral
    "#CFFAFE",  # aqua
    "#FEF9C3",  # cream
    "#E0F2FE",  # ice
    "#F3E8FF",  # lilac
    "#DCFCE7",
    "#FFEDD5",  # peach
]

DAY_NAMES = {"MON": "Monday", "TUE": "Tuesday", "WED": "Wednesday",
             "THU": "Thursday", "FRI": "Friday"}


def _empty_grid() -> pd.DataFrame:
    idx = [f"{s} – {e}" for s, e in TIME_BANDS]
    cols = [DAY_NAMES[d] for d in DAYS]
    return pd.DataFrame("", index=idx, columns=cols)


def build_timetable_grid(selected: list[dict]) -> tuple[pd.DataFrame, dict]:
    """Return (grid_df, color_map) where color_map maps course_code -> color hex."""
    grid = _empty_grid()
    color_map: dict[str, str] = {}
    for i, course in enumerate(selected):
        color_map[course.get("course_code", f"C{i}")] = SOFT_COLORS[i % len(SOFT_COLORS)]

    for course in selected:
        cells = cells_of_course(course)
        for (day, band_idx) in cells:
            row = band_label(band_idx)
            col = DAY_NAMES[day]
            # Determine which slot label matches this cell.
            theory_here = THEORY_GRID[day][band_idx]
            lab_here = LAB_GRID[day][band_idx]
            course_theory_atoms = set((course.get("theory_slot") or "").split("+"))
            course_lab_atoms = set((course.get("lab_slot") or "").split("+"))
            if theory_here and theory_here in course_theory_atoms:
                slot_label = theory_here
                comp = "Theory"
            elif lab_here and lab_here in course_lab_atoms:
                slot_label = lab_here
                comp = "Lab"
            else:
                slot_label = theory_here or lab_here
                comp = "Class"
            cell = (
                f"{course['course_code']}|{course.get('faculty','')}"
                f"|{slot_label}|{comp}"
            )
            grid.at[row, col] = cell
    return grid, color_map


def grid_to_html(grid: pd.DataFrame, color_map: dict[str, str]) -> str:
    """Render the timetable grid as beautiful, self-contained HTML."""
    header_cells = "".join(
        f'<th class="tt-th">{col}</th>' for col in grid.columns
    )
    rows_html = []
    for row_label, row in grid.iterrows():
        cells_html = [f'<td class="tt-time">{row_label}</td>']
        for col in grid.columns:
            v = row[col]
            if v:
                code, fac, slot, comp = v.split("|", 3)
                color = color_map.get(code, "#F3F4F6")
                comp_tag = "T" if comp == "Theory" else ("L" if comp == "Lab" else "•")
                cells_html.append(
                    f'<td class="tt-cell tt-filled" style="background:{color};">'
                    f'<div class="tt-code">{code}</div>'
                    f'<div class="tt-fac">{fac}</div>'
                    f'<div class="tt-slot"><span class="tt-tag">{comp_tag}</span>{slot}</div>'
                    f'</td>'
                )
            else:
                cells_html.append('<td class="tt-cell tt-empty"></td>')
        rows_html.append(f'<tr>{"".join(cells_html)}</tr>')

    return f"""
<div class="tt-wrap">
  <table class="tt">
    <thead>
      <tr><th class="tt-th tt-th-time">Time</th>{header_cells}</tr>
    </thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>
</div>
"""
