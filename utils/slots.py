"""VIT-AP FFCS Slot System — canonical grid (Tue–Sat).

This mirrors the official VIT-AP timetable exactly:
- 5 class days: TUE, WED, THU, FRI, SAT
- Theory has been adjusted to 11 positional blocks to align with the visual matrix gaps.
- Lab has 12 hours per day (6 morning + 6 afternoon), with tighter 50-min bands.
- Some theory cells are "compound" — e.g. `TC1/G1` means the same physical
  time is claimed by two slot names. A course picking either name clashes
  with a course picking the other. We resolve everything to a physical
  minute-interval and check overlap.
"""
from __future__ import annotations

DAYS = ["TUE", "WED", "THU", "FRI", "SAT"]

DAY_NAMES = {
    "TUE": "Tuesday",  "WED": "Wednesday", "THU": "Thursday",
    "FRI": "Friday",   "SAT": "Saturday",
}

# ---------- Physical time bands (minutes since midnight) ----------
# Updated to match the precise vertical column boundaries of the timetable grid.
THEORY_BANDS = [
    (480,  530),   # HR 1:  08:00–08:50
    (540,  590),   # HR 2:  09:00–09:50
    (600,  650),   # HR 3:  10:00–10:50
    (660,  710),   # HR 4:  11:00–11:50
    (720,  770),   # HR 5:  12:00–12:50
    (750,  790),   # HR 6:  12:30–13:10 (Midday Gap/Lunch Tracking Slot)
    (840,  890),   # HR 7:  14:00–14:50
    (900,  950),   # HR 8:  15:00–15:50
    (960,  1010),  # HR 9:  16:00–16:50
    (1020, 1070),  # HR 10: 17:00–17:50
    (1060, 1110),  # HR 11: 17:40–18:30 -> Matches the L40 afternoon block!
]

# Lab: 6 morning + 6 afternoon (12 total). Lunch between LP6 and LP7.
LAB_BANDS = [
    (480,  530),   # HR 1:  08:00–08:50
    (530,  580),   # HR 2:  08:50–09:40
    (590,  640),   # HR 3:  09:50–10:40
    (640,  690),   # HR 4:  10:40–11:30
    (700,  750),   # HR 5:  11:40–12:30
    (750,  790),   # HR 6:  12:30–13:10
    (840,  890),   # HR 7:  14:00–14:50
    (890,  940),   # HR 8:  14:50–15:40
    (950,  1000),  # HR 9:  15:50–16:40
    (1000, 1050),  # HR 10: 16:40–17:30
    (1060, 1110),  # HR 11: 17:40–18:30 -> This is exactly where L40 sits on the grid!
    (1110, 1150),  # HR 12: 18:30–19:10
]

# ---------- Slot grids (as printed on the physical FFCS timetable) ----------
# Empty strings ("") act as crucial positional padding elements to align indices.
THEORY_GRID: dict[str, list[str]] = {
    "TUE": ["TFF1", "A1",     "B1",      "TC1/G1",    "D1",        "", "F2",     "A2",       "B2",      "TC2/G2",   "TDD2"],
    "WED": ["TGG1", "D1",     "F1",      "E1/SC2",    "B1",        "", "D2",     "TF2/G2",   "E2/SC1",  "B2",       "TCC2"],
    "THU": ["TEE1", "C1",     "TD1/TG1", "TAA1/ECS",  "TBB1/CLUB", "", "TE2/SE1", "C2",       "TD2/TG2", "A2",       "TFF2"],
    "FRI": ["TCC1", "TB1",    "TA1",     "F1",        "TE1/SD2",   "", "C2",     "TB2",      "TA2",     "F2",       "TEE2"],
    "SAT": ["TDD1", "E1/SE2", "C1",      "TF1/G1",    "A1",        "", "D2",     "E2/SD1",   "TAA2/ECS", "TBB2/CLUB", "TGG2"],
}

# Explicitly written grids matching structural timetable column locations.
# "" handles structural hour cells that contain no lab slot codes.
LAB_GRID: dict[str, list[str]] = {
    "TUE": ["L1",  "L2",  "L3",  "L4",  "L5",  "L6",  "",    "L31", "L32", "L33", "L34", "L35"],
    "WED": ["L7",  "L8",  "L9",  "L10", "L11", "L12", "",    "L37", "L38", "L39", "L40", "L41"],
    "THU": ["L13", "L14", "L15", "L16", "L17", "L18", "",    "L43", "L44", "L45", "L46", "L47"],
    "FRI": ["L19", "L20", "L21", "L22", "L23", "L24", "",    "L49", "L50", "L51", "L52", "L53"],
    "SAT": ["L25", "L26", "L27", "L28", "L29", "L30", "",    "L55", "L56", "L57", "L58", "L59"],
}


# ---------- Slot atom → list of (day, start_min, end_min) ----------
def _build_slot_intervals() -> dict[str, list[tuple[str, int, int]]]:
    m: dict[str, list[tuple[str, int, int]]] = {}
    for day, cells in THEORY_GRID.items():
        for i, cell in enumerate(cells):
            start, end = THEORY_BANDS[i]
            for atom in cell.split("/"):
                atom = atom.strip().upper()
                if atom:
                    m.setdefault(atom, []).append((day, start, end))
    for day, cells in LAB_GRID.items():
        for i, atom in enumerate(cells):
            # Guard to ensure empty padding strings do not crash or register as valid keys
            if not atom:
                continue
            start, end = LAB_BANDS[i]
            m.setdefault(atom.upper(), []).append((day, start, end))
    return m


SLOT_TO_INTERVALS: dict[str, list[tuple[str, int, int]]] = _build_slot_intervals()


# ---------- Helpers ----------
def parse_slot_string(slot_str: str) -> list[str]:
    """Split a compound slot code like 'A1+TA1+TAA1' or 'L37+L38'."""
    if not slot_str or not isinstance(slot_str, str):
        return []
    return [tok.strip().upper() for tok in slot_str.split("+") if tok.strip()]


def intervals_of_slot(slot_str: str) -> list[tuple[str, int, int]]:
    """Every (day, start_min, end_min) physical interval occupied by the string."""
    out: list[tuple[str, int, int]] = []
    for atom in parse_slot_string(slot_str):
        out.extend(SLOT_TO_INTERVALS.get(atom, []))
    return out


def is_valid_slot(slot_str: str) -> bool:
    atoms = parse_slot_string(slot_str)
    if not atoms:
        return False
    return all(a in SLOT_TO_INTERVALS for a in atoms)


def intervals_overlap(a: tuple[str, int, int], b: tuple[str, int, int]) -> bool:
    """Two intervals overlap iff same day and their [start,end) touch."""
    if a[0] != b[0]:
        return False
    return a[1] < b[2] and b[1] < a[2]


def any_overlap(intervals_a: list, intervals_b: list) -> bool:
    for a in intervals_a:
        for b in intervals_b:
            if intervals_overlap(a, b):
                return True
    return False


def fmt_minutes(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def theory_band_label(idx: int) -> str:
    s, e = THEORY_BANDS[idx]
    return f"{fmt_minutes(s)}–{fmt_minutes(e)}"


def lab_band_label(idx: int) -> str:
    s, e = LAB_BANDS[idx]
    return f"{fmt_minutes(s)}–{fmt_minutes(e)}"


def is_lab_atom(atom: str) -> bool:
    """True if a slot atom is a lab slot (L1..L60)."""
    if not atom:
        return False
    a = atom.upper()
    return a.startswith("L") and a[1:].isdigit()


# Credit inference (for validation / UI hints)
CREDIT_HINTS: dict[int, str] = {
    1: "Single tutorial slot (TA1, TB1, …)",
    2: "Single lecture slot (A1, B1, …)",
    3: "Lecture + tutorial pair (A1+TA1)",
    4: "Lecture + tutorial + tertiary (A1+TA1+TAA1) — or Theory+Lab combo",
}
