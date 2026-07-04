"""Timetable tab — renders the current selection as a beautiful grid."""
from __future__ import annotations
import streamlit as st

from utils.timetable import build_timetable_grid, grid_to_html


def render_timetable_view() -> None:
    st.markdown(
        '<div class="ss-section-title"><h2>Your timetable</h2>'
        '<span class="aside">STEP 04 · TIMETABLE</span></div>',
        unsafe_allow_html=True,
    )

    selected = st.session_state.selected_courses
    if not selected:
        st.markdown(
            '<div class="ss-panel" data-testid="timetable-empty" style="text-align:center;color:var(--muted);">'
            'Add a few courses first — your timetable will appear here.</div>',
            unsafe_allow_html=True,
        )
        return

    grid, colors = build_timetable_grid(selected)
    html = grid_to_html(grid, colors)
    st.markdown(html, unsafe_allow_html=True)

    # Legend
    legend_items = "".join(
        f'<span class="ss-chip"><span style="width:10px;height:10px;border-radius:3px;background:{colors[c["course_code"]]};display:inline-block;margin-right:6px;"></span>{c["course_code"]} · {c["course_name"]}</span>'
        for c in selected
    )
    st.markdown(f'<div class="ss-chips" style="margin-top:14px;">{legend_items}</div>',
                unsafe_allow_html=True)
