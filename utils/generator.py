"""Automatic timetable combination generator."""
from __future__ import annotations
from itertools import product
import pandas as pd
from .data import load_courses, load_faculty, faculty_for_course
from .clash import combo_clash
from .slots import band_start_hour, band_end_hour, slots_to_cells


def _course_type(course_name: str, courses: pd.DataFrame) -> str:
    row = courses[courses["Course Name"] == course_name]
    if row.empty:
        return "Theory"
    return str(row.iloc[0]["Course Type"])


def _credits(course_name: str, courses: pd.DataFrame) -> int:
    row = courses[courses["Course Name"] == course_name]
    if row.empty:
        return 0
    try:
        return int(row.iloc[0]["Credits"])
    except Exception:
        return 0


def build_offerings_for_course(course_name: str) -> list[dict]:
    """Return every valid (theory, lab) offering combination for one course."""
    courses = load_courses()
    ctype = _course_type(course_name, courses).lower()
    theory_df = faculty_for_course(course_name, "Theory")
    lab_df = faculty_for_course(course_name, "Lab")
    credits = _credits(course_name, courses)

    offerings: list[dict] = []
    has_theory = "theory" in ctype and not theory_df.empty
    has_lab = "lab" in ctype and not lab_df.empty

    if has_theory and has_lab:
        for _, t in theory_df.iterrows():
            for _, l in lab_df.iterrows():
                offerings.append({
                    "course_name": course_name,
                    "course_code": _code(course_name, courses),
                    "credits": credits,
                    "faculty": f"{t['Faculty']} / {l['Faculty']}",
                    "theory_slot": t["Slot"],
                    "lab_slot": l["Slot"],
                })
    elif has_theory:
        for _, t in theory_df.iterrows():
            offerings.append({
                "course_name": course_name,
                "course_code": _code(course_name, courses),
                "credits": credits,
                "faculty": t["Faculty"],
                "theory_slot": t["Slot"],
                "lab_slot": "",
            })
    elif has_lab:
        for _, l in lab_df.iterrows():
            offerings.append({
                "course_name": course_name,
                "course_code": _code(course_name, courses),
                "credits": credits,
                "faculty": l["Faculty"],
                "theory_slot": "",
                "lab_slot": l["Slot"],
            })
    return offerings


def _code(course_name: str, courses: pd.DataFrame) -> str:
    row = courses[courses["Course Name"] == course_name]
    return "" if row.empty else str(row.iloc[0]["Course Code"])


def is_day_scholar_valid(combo: list[dict],
                         earliest: float = 9.0, latest: float = 18.0) -> bool:
    """Reject combos with any class starting before 9:00 or ending after 18:00."""
    for off in combo:
        for slot_str in (off.get("theory_slot", ""), off.get("lab_slot", "")):
            if not slot_str:
                continue
            for (_, band_idx) in slots_to_cells(slot_str):
                if band_start_hour(band_idx) < earliest:
                    return False
                if band_end_hour(band_idx) > latest:
                    return False
    return True


def generate_options(course_names: list[str],
                     day_scholar: bool = False,
                     max_options: int = 50) -> list[list[dict]]:
    """Cartesian product of offerings per course, filtered by clashes and mode."""
    if not course_names:
        return []
    per_course = [build_offerings_for_course(c) for c in course_names]
    if any(len(x) == 0 for x in per_course):
        return []

    results: list[list[dict]] = []
    for combo in product(*per_course):
        combo_list = list(combo)
        if combo_clash(combo_list):
            continue
        if day_scholar and not is_day_scholar_valid(combo_list):
            continue
        results.append(combo_list)
        if len(results) >= max_options:
            break
    return results
