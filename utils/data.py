"""CSV data loading (Tue–Sat grid, new faculty schema).

courses.csv columns: Course Code, Course Name, Credits, Course Type
faculty.csv columns: CourseCode, CourseName, Component, FacultyName, Slot
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COURSES_CSV = DATA_DIR / "courses.csv"
FACULTY_CSV = DATA_DIR / "faculty.csv"

REQUIRED_COURSES_COLS = ["Course Code", "Course Name", "Credits", "Course Type"]
# Preferred names — we also accept the legacy schema for backward compat.
REQUIRED_FACULTY_COLS = ["CourseCode", "CourseName", "Component", "FacultyName", "Slot"]

# Aliases for tolerant column matching.
_FACULTY_ALIASES = {
    "CourseCode":  ["CourseCode", "Course Code", "Code"],
    "CourseName":  ["CourseName", "Course Name", "Course"],
    "Component":   ["Component", "Type", "Kind"],
    "FacultyName": ["FacultyName", "Faculty Name", "Faculty", "Instructor"],
    "Slot":        ["Slot", "Slots"],
}


def _read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv(path, dtype=str, keep_default_na=False,
                         encoding="latin-1", engine="python")
    df.columns = [c.strip() for c in df.columns]
    for c in df.columns:
        df[c] = df[c].astype(str).str.strip()
    return df


def _rename_by_alias(df: pd.DataFrame, alias_map: dict[str, list[str]]) -> pd.DataFrame:
    lower_cols = {c.lower(): c for c in df.columns}
    rename: dict[str, str] = {}
    for canon, options in alias_map.items():
        for opt in options:
            if opt.lower() in lower_cols and lower_cols[opt.lower()] != canon:
                rename[lower_cols[opt.lower()]] = canon
                break
    return df.rename(columns=rename)


@st.cache_data(show_spinner=False)
def load_courses() -> pd.DataFrame:
    df = _read_csv_safe(COURSES_CSV)
    if df.empty:
        return pd.DataFrame(columns=REQUIRED_COURSES_COLS)

    df = _rename_by_alias(df, {
        "Course Code": ["Course Code", "CourseCode", "Code"],
        "Course Name": ["Course Name", "CourseName", "Course"],
        "Credits":     ["Credits", "Credit"],
        "Course Type": ["Course Type", "CourseType", "Type"],
    })

    for col in REQUIRED_COURSES_COLS:
        if col not in df.columns:
            df[col] = ""

    def _to_int(x: str) -> int:
        try:
            return int(float(x))
        except Exception:
            return 0
    df["Credits"] = df["Credits"].apply(_to_int)

    df = df[df["Course Code"] != ""]
    df = df.drop_duplicates(subset=["Course Code"], keep="first").reset_index(drop=True)
    return df


@st.cache_data(show_spinner=False)
def load_faculty() -> pd.DataFrame:
    df = _read_csv_safe(FACULTY_CSV)
    if df.empty:
        return pd.DataFrame(columns=REQUIRED_FACULTY_COLS)

    df = _rename_by_alias(df, _FACULTY_ALIASES)
    for col in REQUIRED_FACULTY_COLS:
        if col not in df.columns:
            df[col] = ""

    df["Component"] = df["Component"].str.title().replace({"Lecture": "Theory"})
    df = df[df["Slot"] != ""]

    # If CourseCode missing, backfill from CourseName ↔ courses.csv
    if (df["CourseCode"] == "").any():
        courses = load_courses()
        if not courses.empty:
            name_to_code = dict(zip(courses["Course Name"].str.casefold(),
                                    courses["Course Code"]))
            df.loc[df["CourseCode"] == "", "CourseCode"] = df.loc[
                df["CourseCode"] == "", "CourseName"
            ].str.casefold().map(name_to_code).fillna("")

    return df.reset_index(drop=True)


def faculty_for_course(course_code: str, component: str) -> pd.DataFrame:
    fac = load_faculty()
    if fac.empty:
        return fac
    return fac[
        (fac["CourseCode"].str.casefold() == str(course_code).casefold())
        & (fac["Component"].str.casefold() == component.casefold())
    ].reset_index(drop=True)


def data_status() -> dict:
    courses = load_courses()
    faculty = load_faculty()
    return {
        "num_courses":          int(len(courses)),
        "num_faculty":          int(faculty["FacultyName"].nunique()) if not faculty.empty else 0,
        "num_faculty_offerings": int(len(faculty)),
        "courses_csv_present": COURSES_CSV.exists(),
        "faculty_csv_present": FACULTY_CSV.exists(),
    }
