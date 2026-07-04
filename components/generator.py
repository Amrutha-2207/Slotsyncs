"""Automatic timetable generator — cartesian product with clash filtering."""
from __future__ import annotations
import streamlit as st

from utils.generator import generate_options
from utils.timetable import grid_to_html


def _course_list_from_selection() -> list[str]:
    return [c["course_code"] for c in st.session_state.selected_courses]


def render_generator() -> None:
    st.markdown(
        '<div class="ss-section-title"><h2>Auto-generate options</h2>'
        '<span class="aside">STEP 05 · GENERATOR</span></div>',
        unsafe_allow_html=True,
    )

    selected = st.session_state.selected_courses
    if not selected:
        st.markdown(
            '<div class="ss-panel" style="text-align:center;color:var(--muted);">'
            'Select at least one course to generate alternatives.</div>',
            unsafe_allow_html=True,
        )
        return

    day_scholar = st.session_state.get("day_scholar_mode", False)
    course_codes = _course_list_from_selection()

    with st.spinner("Crunching every valid combination…"):
        options = generate_options(course_codes, day_scholar=day_scholar, max_options=30)

    label_mode = "Day Scholar" if day_scholar else "Hosteller"
    st.markdown(
        f'<div class="ss-mono ss-mute" style="font-size:12px;letter-spacing:.12em;margin-bottom:14px;" data-testid="gen-summary">'
        f'{len(options)} VALID OPTIONS · MODE · {label_mode.upper()}</div>',
        unsafe_allow_html=True,
    )

    if not options:
        st.markdown(
            '<div class="ss-clash"><span class="icn">⚠️</span>'
            '<div>No clash-free combination exists for the current course set'
            f'{" under Day-Scholar constraints" if day_scholar else ""}.</div></div>',
            unsafe_allow_html=True,
        )
        return

    for i, combo in enumerate(options, start=1):
        credits = sum(int(o.get("credits", 0)) for o in combo)
        with st.container():
            st.markdown(
                f'''
                <div class="ss-option-card" data-testid="option-{i}">
                  <div class="ss-option-head">
                    <div class="ss-option-num">Option {i:02d}</div>
                    <div class="ss-option-meta">{len(combo)} COURSES · {credits} CREDITS</div>
                  </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

            with st.expander("Preview details", expanded=(i == 1)):
                items = "".join(
                    f'<li><b>{o["course_code"]}</b> — {o["course_name"]} '
                    f'<span class="ss-mono ss-mute">'
                    f'· {o.get("theory_slot") or "—"} · {o.get("lab_slot") or "—"}'
                    f'</span><br/>'
                    f'<span class="ss-mute" style="font-size:12px;">👤 {o["faculty"]}</span></li>'
                    for o in combo
                )
                st.markdown(f'<div class="ss-option-body"><ul>{items}</ul></div>',
                            unsafe_allow_html=True)

                grid_html = grid_to_html(combo)
                st.markdown(grid_html, unsafe_allow_html=True)

                if st.button("Apply this option", key=f"apply_{i}",
                             type="primary", use_container_width=True):
                    st.session_state.selected_courses = combo
                    st.toast(f"Applied Option {i:02d}", icon="✅")
                    st.rerun()
