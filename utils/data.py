"""CSV data loading with caching, error tolerance, and normalisation."""
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

COURSES_CSV = DATA_DIR / "courses.csv"
FACULTY_CSV = DATA_DIR / "faculty.csv"

REQUIRED_COURSES_COLS = ["Course Code", "Course Name", "Credits", "Course Type"]
REQUIRED_FACULTY_COLS = ["Course", "Component", "Faculty", "Slot"]


def _read_csv_safe(path: Path, required_cols: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=required_cols)
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv(path, dtype=str, keep_default_na=False,
                         encoding="latin-1", engine="python")
    df.columns = [c.strip() for c in df.columns]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df


@st.cache_data(show_spinner=False)
def load_courses() -> pd.DataFrame:
    df = _read_csv_safe(COURSES_CSV, REQUIRED_COURSES_COLS)
    if df.empty:
        return df
    # Normalise credits to int where possible
    def _to_int(x: str) -> int:
        try:
            return int(float(x))
        except Exception:
            return 0
    df["Credits"] = df["Credits"].apply(_to_int)
    df = df.drop_duplicates(subset=["Course Code"], keep="first")
    return df.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_faculty() -> pd.DataFrame:
    df = _read_csv_safe(FACULTY_CSV, REQUIRED_FACULTY_COLS)
    if df.empty:
        return df
    df["Component"] = df["Component"].str.title().replace({"Lecture": "Theory"})
    df = df[df["Slot"] != ""]
    return df.reset_index(drop=True)


def faculty_for_course(course_name: str, component: str) -> pd.DataFrame:
    fac = load_faculty()
    if fac.empty:
        return fac
    return fac[
        (fac["Course"].str.casefold() == course_name.casefold())
        & (fac["Component"].str.casefold() == component.casefold())
    ].reset_index(drop=True)


def data_status() -> dict:
    """Return a small status dict useful for the hero stats."""
    courses = load_courses()
    faculty = load_faculty()
    return {
        "num_courses": int(len(courses)),
        "num_faculty": int(faculty["Faculty"].nunique()) if not faculty.empty else 0,
        "courses_csv_present": COURSES_CSV.exists(),
        "faculty_csv_present": FACULTY_CSV.exists(),
    }
