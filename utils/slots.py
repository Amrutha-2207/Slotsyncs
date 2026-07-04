"""VIT-AP FFCS Slot System — canonical grid & helpers."""
from __future__ import annotations

# Standard VIT-AP FFCS timetable grid.
# Each day has 12 rows (11 class rows + 1 lunch). Each cell can hold a
# theory slot and a lab slot that share the same physical time band.

DAYS = ["MON", "TUE", "WED", "THU", "FRI"]

# 12 time bands (index 0..11); a lunch band separates morning/afternoon.
TIME_BANDS = [
    ("08:00", "08:50"),
    ("08:55", "09:45"),
    ("09:50", "10:40"),
    ("10:45", "11:35"),
    ("11:40", "12:30"),
    ("12:35", "13:25"),   # morning tail (mostly Lab-only)
    ("14:00", "14:50"),
    ("14:55", "15:45"),
    ("15:50", "16:40"),
    ("16:45", "17:35"),
    ("17:40", "18:30"),
    ("18:35", "19:25"),   # afternoon tail (mostly Lab-only)
]

LUNCH_LABEL = ("13:25", "14:00")

# Theory slot layout: [day][band] -> theory slot code ("" if none)
# Bands 0..4 morning theory, band 5 no theory, bands 6..10 afternoon, band 11 none.
THEORY_GRID = {
    "MON": ["A1",  "F1",   "D1",   "TB1",  "TG1",  "",  "A2",  "F2",   "D2",   "TB2",  "TG2",  ""],
    "TUE": ["B1",  "G1",   "E1",   "TC1",  "TAA1", "",  "B2",  "G2",   "E2",   "TC2",  "TAA2", ""],
    "WED": ["C1",  "A1",   "F1",   "TD1",  "TBB1", "",  "C2",  "A2",   "F2",   "TD2",  "TBB2", ""],
    "THU": ["D1",  "B1",   "G1",   "TE1",  "TCC1", "",  "D2",  "B2",   "G2",   "TE2",  "TCC2", ""],
    "FRI": ["E1",  "C1",   "A1",   "TF1",  "TDD1", "",  "E2",  "C2",   "A2",   "TF2",  "TDD2", ""],
}

# Lab slot layout: L1..L60, six per day per half.
LAB_GRID = {
    "MON": ["L1",  "L2",  "L3",  "L4",  "L5",  "L6",   "L31", "L32", "L33", "L34", "L35", "L36"],
    "TUE": ["L7",  "L8",  "L9",  "L10", "L11", "L12",  "L37", "L38", "L39", "L40", "L41", "L42"],
    "WED": ["L13", "L14", "L15", "L16", "L17", "L18",  "L43", "L44", "L45", "L46", "L47", "L48"],
    "THU": ["L19", "L20", "L21", "L22", "L23", "L24",  "L49", "L50", "L51", "L52", "L53", "L54"],
    "FRI": ["L25", "L26", "L27", "L28", "L29", "L30",  "L55", "L56", "L57", "L58", "L59", "L60"],
}


def _build_slot_to_cells() -> dict[str, list[tuple[str, int]]]:
    m: dict[str, list[tuple[str, int]]] = {}
    for day in DAYS:
        for i, s in enumerate(THEORY_GRID[day]):
            if s:
                m.setdefault(s, []).append((day, i))
        for i, s in enumerate(LAB_GRID[day]):
            if s:
                m.setdefault(s, []).append((day, i))
    return m


SLOT_TO_CELLS: dict[str, list[tuple[str, int]]] = _build_slot_to_cells()


def parse_slot_string(slot_str: str) -> list[str]:
    """Split a compound slot like 'A1+TA1+TAA1' or 'L37+L38' into atoms."""
    if not slot_str or not isinstance(slot_str, str):
        return []
    return [tok.strip().upper() for tok in slot_str.split("+") if tok.strip()]


def slots_to_cells(slot_str: str) -> set[tuple[str, int]]:
    """Return the set of (day, band_idx) cells occupied by a compound slot."""
    cells: set[tuple[str, int]] = set()
    for atom in parse_slot_string(slot_str):
        for cell in SLOT_TO_CELLS.get(atom, []):
            cells.add(cell)
    return cells


def is_valid_slot(slot_str: str) -> bool:
    atoms = parse_slot_string(slot_str)
    if not atoms:
        return False
    return all(a in SLOT_TO_CELLS for a in atoms)


def band_label(idx: int) -> str:
    s, e = TIME_BANDS[idx]
    return f"{s} – {e}"


def band_start_hour(idx: int) -> float:
    """Return the start time as a float hour (e.g. 08:55 -> 8.916)."""
    s, _ = TIME_BANDS[idx]
    h, m = map(int, s.split(":"))
    return h + m / 60.0


def band_end_hour(idx: int) -> float:
    _, e = TIME_BANDS[idx]
    h, m = map(int, e.split(":"))
    return h + m / 60.0
