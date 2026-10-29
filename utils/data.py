
"""CSV data loading (Tue–Sat grid, new faculty schema).

courses.csv columns:
    Course Code, Course Name, Credits, Course Type

faculty.csv columns:
    CourseCode, CourseName, Component, FacultyName, Slot
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from utils.slots import intervals_of_slot


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COURSES_CSV = DATA_DIR / "courses.csv"
FACULTY_CSV = DATA_DIR / "faculty.csv"

REQUIRED_COURSES_COLS = [
    "Course Code",
    "Course Name",
    "Credits",
    "Course Type",
]

REQUIRED_FACULTY_COLS = [
    "CourseCode",
    "CourseName",
    "Component",
    "FacultyName",
    "Slot",
]

# Alternative column names accepted for compatibility.
_FACULTY_ALIASES = {
    "CourseCode": ["CourseCode", "Course Code", "Code"],
    "CourseName": ["CourseName", "Course Name", "Course"],
    "Component": ["Component", "Type", "Kind"],
    "FacultyName": ["FacultyName", "Faculty Name", "Faculty", "Instructor"],
    "Slot": ["Slot", "Slots"],
}


def _read_csv_safe(path: Path) -> pd.DataFrame:
    """Read a CSV safely and normalize whitespace."""
    if not path.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
        )
    except Exception:
        df = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
            encoding="latin-1",
            engine="python",
        )

    df.columns = [column.strip() for column in df.columns]

    for column in df.columns:
        df[column] = df[column].astype(str).str.strip()

    return df


def _rename_by_alias(
    df: pd.DataFrame,
    alias_map: dict[str, list[str]],
) -> pd.DataFrame:
    """Rename recognized column aliases to canonical column names."""
    lower_cols = {column.lower(): column for column in df.columns}
    rename: dict[str, str] = {}

    for canonical, options in alias_map.items():
        for option in options:
            original = lower_cols.get(option.lower())

            if original is not None and original != canonical:
                rename[original] = canonical
                break

    return df.rename(columns=rename)


@st.cache_data(show_spinner=False)
def load_courses() -> pd.DataFrame:
    """Load and normalize course information."""
    df = _read_csv_safe(COURSES_CSV)

    if df.empty:
        return pd.DataFrame(columns=REQUIRED_COURSES_COLS)

    df = _rename_by_alias(
        df,
        {
            "Course Code": ["Course Code", "CourseCode", "Code"],
            "Course Name": ["Course Name", "CourseName", "Course"],
            "Credits": ["Credits", "Credit"],
            "Course Type": ["Course Type", "CourseType", "Type"],
        },
    )

    for column in REQUIRED_COURSES_COLS:
        if column not in df.columns:
            df[column] = ""

    def to_int(value: str) -> int:
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0

    df["Credits"] = df["Credits"].apply(to_int)
    df = df[df["Course Code"] != ""]
    df = df.drop_duplicates(
        subset=["Course Code"],
        keep="first",
    ).reset_index(drop=True)

    return df


@st.cache_data(show_spinner=False)
def load_faculty() -> pd.DataFrame:
    """Load and normalize faculty offerings."""
    df = _read_csv_safe(FACULTY_CSV)

    if df.empty:
        return pd.DataFrame(columns=REQUIRED_FACULTY_COLS)

    df = _rename_by_alias(df, _FACULTY_ALIASES)

    for column in REQUIRED_FACULTY_COLS:
        if column not in df.columns:
            df[column] = ""

    df["Component"] = (
        df["Component"]
        .str.title()
        .replace({"Lecture": "Theory"})
    )

    df = df[df["Slot"] != ""]

    # Fill missing course codes by matching course names.
    if (df["CourseCode"] == "").any():
        courses = load_courses()

        if not courses.empty:
            name_to_code = dict(
                zip(
                    courses["Course Name"].str.casefold(),
                    courses["Course Code"],
                )
            )

            missing_code = df["CourseCode"] == ""

            df.loc[missing_code, "CourseCode"] = (
                df.loc[missing_code, "CourseName"]
                .str.casefold()
                .map(name_to_code)
                .fillna("")
            )

    return df.reset_index(drop=True)


def is_day_scholar_slot(slot: str) -> bool:
    """Return True if every slot interval is within 9 AM–6 PM."""
    intervals = intervals_of_slot(slot)

    if not intervals:
        return False

    return all(
        start >= 9 * 60 and end <= 18 * 60
        for _, start, end in intervals
    )


def faculty_for_course(
    course_code: str,
    component: str,
) -> pd.DataFrame:
    """Get faculty offerings for a course and component."""
    fac = load_faculty()

    if fac.empty:
        return fac

    result = fac[
        (fac["CourseCode"].str.casefold() == str(course_code).casefold())
        & (
            fac["Component"].str.casefold()
            == str(component).casefold()
        )
    ].reset_index(drop=True)

    # Filter offerings when Day Scholar Mode is enabled.
    if st.session_state.get("day_scholar_mode", False):
        result = result[
            result["Slot"].apply(is_day_scholar_slot)
        ].reset_index(drop=True)

    return result


def data_status() -> dict:
    """Return basic information about the loaded CSV files."""
    courses = load_courses()
    faculty = load_faculty()

    return {
        "num_courses": int(len(courses)),
        "num_faculty": (
            int(faculty["FacultyName"].nunique())
            if not faculty.empty
            else 0
        ),
        "num_faculty_offerings": int(len(faculty)),
        "courses_csv_present": COURSES_CSV.exists(),
        "faculty_csv_present": FACULTY_CSV.exists(),
    }
