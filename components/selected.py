"""Selected-courses panel with edit/delete and totals."""
from __future__ import annotations
import streamlit as st

from utils.timetable import SOFT_COLORS


def _swatch(i: int) -> str:
    return SOFT_COLORS[i % len(SOFT_COLORS)]


def render_selected_panel() -> None:
    selected = st.session_state.selected_courses
    st.markdown(
        '<div class="ss-section-title"><h2>Your selection</h2>'
        '<span class="aside">STEP 03 · SELECTED COURSES</span></div>',
        unsafe_allow_html=True,
    )

    if not selected:
        st.markdown(
            '<div class="ss-panel" data-testid="selected-empty" style="text-align:center;color:var(--muted);">'
            'No courses picked yet. Search above and add your first course.</div>',
            unsafe_allow_html=True,
        )
        return

    total_credits = sum(int(c.get("credits", 0)) for c in selected)

    for i, c in enumerate(selected):
        code = c["course_code"]
        theory = c.get("theory_slot") or "—"
        lab = c.get("lab_slot") or "—"
        fac = c.get("faculty") or "—"
        color = _swatch(i)
        left_col, right_col = st.columns([6, 1])
        with left_col:
            st.markdown(
                f'''
                <div class="ss-selected" data-testid="selected-{code}"
                     style="border-left: 4px solid {color};">
                  <div class="left">
                    <div class="code">{code} · {c.get("credits",0)} credits</div>
                    <div class="name">{c["course_name"]}</div>
                    <div class="meta">
                      <span>👤 {fac}</span>
                      <span>THEORY · {theory}</span>
                      <span>LAB · {lab}</span>
                    </div>
                  </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )
        with right_col:
            st.write("")
            b1, b2 = st.columns(2)
            with b1:
                if st.button("✏", key=f"edit_{code}", help="Edit this course",
                             use_container_width=True):
                    st.session_state["search_q"] = c["course_name"]
                    st.session_state["_scroll_target"] = "search"
                    st.rerun()
            with b2:
                if st.button("🗑", key=f"del_{code}", help="Remove this course",
                             use_container_width=True):
                    st.session_state.selected_courses = [
                        x for x in selected if x["course_code"] != code
                    ]
                    st.toast(f"Removed {code}", icon="🗑️")
                    st.rerun()

    st.markdown(
        f'''
        <div class="ss-panel" data-testid="selected-summary"
             style="margin-top:8px;display:flex;justify-content:space-between;align-items:center;">
          <div class="ss-mono ss-mute" style="font-size:12px;letter-spacing:.12em;">
            {len(selected)} COURSES SELECTED
          </div>
          <div>
            <span class="ss-mono ss-mute" style="font-size:12px;letter-spacing:.12em;">TOTAL CREDITS</span>
            <span style="font-family:'Instrument Serif',serif;font-size:28px;margin-left:10px;">{total_credits}</span>
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
