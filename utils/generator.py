"""Automatic timetable combination generator (Tue–Sat)."""
from __future__ import annotations
from itertools import product
import pandas as pd

from .data import load_courses, faculty_for_course
from .clash import combo_clash
from .slots import intervals_of_slot


def _course_row(course_code: str, courses: pd.DataFrame) -> pd.Series | None:
    row = courses[courses["Course Code"] == course_code]
    return None if row.empty else row.iloc[0]


def build_offerings_for_course(course_code: str) -> list[dict]:
    """Every (theory, lab) offering combination for one course."""
    courses = load_courses()
    row = _course_row(course_code, courses)
    if row is None:
        return []

    course_name = str(row["Course Name"])
    credits = int(row["Credits"]) if str(row["Credits"]).isdigit() else 0
    ctype = str(row["Course Type"]).lower()

    theory_df = faculty_for_course(course_code, "Theory")
    lab_df = faculty_for_course(course_code, "Lab")

    has_theory = ("theory" in ctype and not theory_df.empty) or (not theory_df.empty and "lab" not in ctype)
    has_lab = "lab" in ctype and not lab_df.empty

    offerings: list[dict] = []

    if has_theory and has_lab:
        for _, t in theory_df.iterrows():
            for _, l in lab_df.iterrows():
                offerings.append(_offering(
                    course_code, course_name, credits,
                    t["FacultyName"], t["Slot"],
                    l["FacultyName"], l["Slot"],
                ))
    elif has_theory:
        for _, t in theory_df.iterrows():
            offerings.append(_offering(
                course_code, course_name, credits,
                t["FacultyName"], t["Slot"], "", "",
            ))
    elif has_lab:
        for _, l in lab_df.iterrows():
            offerings.append(_offering(
                course_code, course_name, credits,
                "", "", l["FacultyName"], l["Slot"],
            ))
    return offerings


def _offering(code: str, name: str, credits: int,
              tfac: str, tslot: str, lfac: str, lslot: str) -> dict:
    if tfac and lfac:
        faculty = f"{tfac}  ·  {lfac}"
    else:
        faculty = tfac or lfac
    return {
        "course_code":    code,
        "course_name":    name,
        "credits":        credits,
        "faculty":        faculty,
        "faculty_theory": tfac,
        "faculty_lab":    lfac,
        "theory_slot":    tslot,
        "lab_slot":       lslot,
    }


def is_day_scholar_valid(combo: list[dict],
                         earliest: int = 9 * 60, latest: int = 18 * 60) -> bool:
    """Reject combos with any class starting before 09:00 or ending after 18:00."""
    for off in combo:
        for slot_str in (off.get("theory_slot", ""), off.get("lab_slot", "")):
            if not slot_str:
                continue
            for (_, start, end) in intervals_of_slot(slot_str):
                if start < earliest:
                    return False
                if end > latest:
                    return False
    return True


def generate_options(course_codes: list[str],
                     day_scholar: bool = False,
                     max_options: int = 30) -> list[list[dict]]:
    if not course_codes:
        return []
    per_course = [build_offerings_for_course(c) for c in course_codes]
    if any(len(x) == 0 for x in per_course):
        return []

    out: list[list[dict]] = []
    for combo in product(*per_course):
        combo_list = list(combo)
        if combo_clash(combo_list):
            continue
        if day_scholar and not is_day_scholar_valid(combo_list):
            continue
        out.append(combo_list)
        if len(out) >= max_options:
            break
    return out
