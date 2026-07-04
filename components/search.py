"""Search + course card + faculty selection + Add Course flow."""
from __future__ import annotations
import pandas as pd
import streamlit as st

from utils.data import load_courses, faculty_for_course
from utils.clash import clashes_with, has_internal_clash
from utils.slots import parse_slot_string


def _matches(row, q: str) -> bool:
    if not q:
        return True
    q = q.lower()
    return (
        q in str(row["Course Name"]).lower()
        or q in str(row["Course Code"]).lower()
    )


def _fmt_option(slot: str, faculty: str, conflicts: list[str]) -> str:
    if conflicts:
        return f"🟠  {slot} — {faculty}   [clash · {', '.join(conflicts)}]"
    return f"🟢  {slot} — {faculty}"


def _selected_by_code(code: str) -> dict | None:
    for c in st.session_state.selected_courses:
        if c["course_code"] == code:
            return c
    return None


def _add_or_update(course: dict) -> None:
    exists = _selected_by_code(course["course_code"])
    if exists:
        exists.update(course)
        st.toast(f"Updated {course['course_code']}", icon="✏️")
    else:
        st.session_state.selected_courses.append(course)
        st.toast(f"Added {course['course_code']}", icon="✅")


def render_search_and_add() -> None:
    courses = load_courses()
    if courses.empty:
        st.warning("`data/courses.csv` is missing or empty. Add it to begin.")
        return

    st.markdown(
        '<div class="ss-section-title"><h2>Search a course</h2>'
        '<span class="aside">STEP 01 · SEARCH</span></div>',
        unsafe_allow_html=True,
    )

    q = st.text_input(
        "Search",
        key="search_q",
        placeholder="Search by course name or code (e.g. AI or CSE1002)…",
        label_visibility="collapsed",
    )

    filtered = courses[courses.apply(lambda r: _matches(r, q), axis=1)]

    if q and filtered.empty:
        st.info("No courses match your search.")
        return

    st.markdown(
        f'<div class="ss-mono" style="color:var(--muted);font-size:12px;margin:6px 0 14px">'
        f'{len(filtered)} of {len(courses)} courses'
        f'</div>',
        unsafe_allow_html=True,
    )

    for _, row in filtered.iterrows():
        _render_course_card(row)


def _render_course_card(row: pd.Series) -> None:
    code = str(row["Course Code"])
    name = str(row["Course Name"])
    credits = int(row["Credits"]) if str(row["Credits"]).isdigit() else row["Credits"]
    ctype = str(row["Course Type"]).lower()

    already = _selected_by_code(code)
    with st.expander(f"{code}  ·  {name}"):
        # Meta row (kept intentionally compact — expander title already shows name).
        already_pill = (
            '<span class="ss-course-badge" style="background:#F0FDF4;color:#166534;'
            'border-color:#BBF7D0;">Selected</span>' if already else ''
        )
        meta_html = (
            '<div class="ss-course-meta" style="margin-bottom:10px;">'
            f'<span>{credits} credits</span>'
            f'<span>·</span><span>{row["Course Type"]}</span>'
            f'{already_pill}'
            '</div>'
        )
        st.markdown(meta_html, unsafe_allow_html=True)

        theory_df = faculty_for_course(code, "Theory")
        lab_df = faculty_for_course(code, "Lab") if "lab" in ctype else pd.DataFrame()

        theory_choice = None
        lab_choice = None

        others = [c for c in st.session_state.selected_courses if c["course_code"] != code]

        # Layout columns: 2 for Theory+Lab courses, 1 otherwise.
        want_theory = ("theory" in ctype) or (not theory_df.empty)
        want_lab = ("lab" in ctype)
        cols = st.columns(2 if (want_theory and want_lab) else 1)
        col_idx = 0

        if want_theory:
            with cols[col_idx]:
                st.markdown('<div class="ss-mono" style="font-size:11px;letter-spacing:.14em;color:var(--muted);text-transform:uppercase;margin-bottom:6px;">Theory</div>', unsafe_allow_html=True)
                if theory_df.empty:
                    st.markdown('<div class="ss-mute" style="font-size:13px;">No theory offerings in faculty.csv yet.</div>', unsafe_allow_html=True)
                else:
                    options = []
                    values = []
                    for _, r in theory_df.iterrows():
                        conflicts = clashes_with(r["Slot"], others)
                        options.append(_fmt_option(r["Slot"], r["FacultyName"], conflicts))
                        values.append((r["Slot"], r["FacultyName"], conflicts))
                    # preselect current if editing
                    default_idx = 0
                    if already and already.get("theory_slot"):
                        for i, v in enumerate(values):
                            if v[0] == already["theory_slot"] and v[1] == already.get("faculty_theory", already.get("faculty", "")):
                                default_idx = i
                                break
                    picked = st.selectbox(
                        "Theory option", options, index=default_idx,
                        key=f"theory_{code}", label_visibility="collapsed",
                    )
                    theory_choice = values[options.index(picked)]
            col_idx += 1

        if want_lab:
            with cols[col_idx]:
                st.markdown('<div class="ss-mono" style="font-size:11px;letter-spacing:.14em;color:var(--muted);text-transform:uppercase;margin-bottom:6px;">Lab</div>', unsafe_allow_html=True)
                if lab_df.empty:
                    st.markdown('<div class="ss-mute" style="font-size:13px;">No lab offerings in faculty.csv yet.</div>', unsafe_allow_html=True)
                else:
                    options = []
                    values = []
                    for _, r in lab_df.iterrows():
                        conflicts = clashes_with(r["Slot"], others)
                        options.append(_fmt_option(r["Slot"], r["FacultyName"], conflicts))
                        values.append((r["Slot"], r["FacultyName"], conflicts))
                    default_idx = 0
                    if already and already.get("lab_slot"):
                        for i, v in enumerate(values):
                            if v[0] == already["lab_slot"] and v[1] == already.get("faculty_lab", already.get("faculty", "")):
                                default_idx = i
                                break
                    picked = st.selectbox(
                        "Lab option", options, index=default_idx,
                        key=f"lab_{code}", label_visibility="collapsed",
                    )
                    lab_choice = values[options.index(picked)]

        # ------- Clash summary -------
        chosen_theory_slot = theory_choice[0] if theory_choice else ""
        chosen_lab_slot = lab_choice[0] if lab_choice else ""
        conflict_codes: set[str] = set()
        if theory_choice:
            conflict_codes |= set(theory_choice[2])
        if lab_choice:
            conflict_codes |= set(lab_choice[2])
        internal = has_internal_clash(chosen_theory_slot, chosen_lab_slot)

        if conflict_codes or internal:
            names_map = {c["course_code"]: c["course_name"] for c in st.session_state.selected_courses}
            reasons = []
            if internal:
                reasons.append("This course's theory and lab slots overlap")
            for c in sorted(conflict_codes):
                reasons.append(f"conflicts with <b>{names_map.get(c, c)}</b>")
            reason_txt = " · ".join(reasons)
            st.markdown(
                f'<div class="ss-clash" data-testid="clash-warn-{code}">'
                f'<span class="icn">⚠️</span>'
                f'<div><b>Clash detected.</b><br/><span style="opacity:.9">{reason_txt}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="ss-ok" data-testid="clash-ok">✓ No clash with your current selection.</div>',
                unsafe_allow_html=True,
            )

        # ------- Action -------
        b_cols = st.columns([1, 1, 3])
        with b_cols[0]:
            label = "Update Course" if already else "Add Course"
            if st.button(label, type="primary", key=f"add_{code}", use_container_width=True):
                if not theory_choice and not lab_choice:
                    st.warning("Pick at least one component (theory or lab).")
                else:
                    faculty_str = ""
                    if theory_choice and lab_choice:
                        faculty_str = f"{theory_choice[1]}  ·  {lab_choice[1]}"
                    elif theory_choice:
                        faculty_str = theory_choice[1]
                    elif lab_choice:
                        faculty_str = lab_choice[1]
                    _add_or_update({
                        "course_code": code,
                        "course_name": name,
                        "credits": int(credits) if isinstance(credits, int) else 0,
                        "theory_slot": chosen_theory_slot,
                        "lab_slot": chosen_lab_slot,
                        "faculty": faculty_str,
                        "faculty_theory": theory_choice[1] if theory_choice else "",
                        "faculty_lab": lab_choice[1] if lab_choice else "",
                    })
                    st.rerun()

        with b_cols[1]:
            if already and st.button("Remove", key=f"rm_{code}", use_container_width=True):
                st.session_state.selected_courses = [
                    c for c in st.session_state.selected_courses if c["course_code"] != code
                ]
                st.toast(f"Removed {code}", icon="🗑️")
                st.rerun()
