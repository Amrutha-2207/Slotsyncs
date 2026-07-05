"""SlotSync — a smart FFCS Planner for VIT-AP.

Single-page Streamlit app organised into tabs so students reach their
final timetable in the fewest possible clicks.
"""
from __future__ import annotations
import streamlit as st

from utils.style import inject_css
from utils.counter import register_visit
from components.hero import render_hero, render_navbar
from components.search import render_search_and_add
from components.selected import render_selected_panel
from components.timetable_view import render_timetable_view
from components.generator import render_generator
from components.export import render_export


st.set_page_config(
    page_title="SlotSync — VIT-AP FFCS Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "SlotSync — a calm FFCS planner for VIT-AP students.",
    },
)

inject_css()

# ---------------- Session state ----------------
if "selected_courses" not in st.session_state:
    st.session_state.selected_courses = []

# Count this visitor (once per browser session).
register_visit()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown(
        '<div style="padding: 8px 4px 16px 4px;">'
        '<div class="ss-brand"><span class="ss-brand-mark">S</span><span>SlotSync</span></div>'
        '<div class="ss-mono ss-mute" style="font-size:11px;letter-spacing:.14em;margin-top:4px;">'
        'VIT-AP · FFCS PLANNER</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="ss-hr"/>', unsafe_allow_html=True)

    st.markdown('<div class="ss-mono ss-mute" style="font-size:11px;letter-spacing:.14em;margin-bottom:6px;">SESSION SUMMARY</div>',
                unsafe_allow_html=True)
    n = len(st.session_state.selected_courses)
    
    # Safe handling logic to prevent integer casting crashes from raw datasets
    total_credits = 0
    for c in st.session_state.selected_courses:
        try:
            total_credits += int(c.get("credits", 0))
        except (ValueError, TypeError):
            pass

    st.markdown(
        f'<div style="font-family:\'Instrument Serif\',serif;font-size:24px;letter-spacing:-0.02em;">'
        f'{n} courses picked<br/><span style="color:var(--muted);font-size:16px;">{total_credits} total credits</span></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.selected_courses:
        if st.button("Clear all courses", use_container_width=True, key="clear-all"):
            st.session_state.selected_courses = []
            st.toast("Cleared selection", icon="🧹")
            st.rerun()

    st.markdown('<hr class="ss-hr"/>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ss-mono ss-mute" style="font-size:11px;letter-spacing:.14em;line-height:1.7;">'
        'STATUS · PLATFORM ONLINE<br/>GRID · VIT-AP FFCS SPECIFICATION'
        '</div>',
        unsafe_allow_html=True,
    )

# ---------------- Main ----------------
render_navbar()
render_hero()

st.markdown('<hr class="ss-hr"/>', unsafe_allow_html=True)

tab_search, tab_selected, tab_tt, tab_gen, tab_export = st.tabs(
    ["Search & Add", "Selected Courses", "Timetable", "Auto-Generate", "Export"]
)

with tab_search:
    render_search_and_add()

with tab_selected:
    render_selected_panel()

with tab_tt:
    render_timetable_view()

with tab_gen:
    render_generator()

with tab_export:
    render_export()

st.markdown(
    '<div class="ss-foot">SLOTSYNC · BUILT WITH CARE FOR VIT-AP · v1.0</div>',
    unsafe_allow_html=True,
)

