"""Hero section, stats and feature chips."""
from __future__ import annotations
import streamlit as st

from utils.data import data_status
from utils.counter import peek_visits

_CHIP_ICONS = {
    "Clash Detection": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4"/><path d="M12 17h.01"/><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/></svg>',
    "Faculty Selection": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "Timetable Generator": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>',
    "Export Timetable": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
}


def _fmt_count(n: int) -> str:
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


def render_navbar() -> None:
    st.markdown(
        """
        <div class="ss-nav" data-testid="ss-navbar">
          <div class="ss-brand">
            <span class="ss-brand-mark">S</span>
            <span>SlotSync</span>
          </div>
          <div class="ss-nav-meta">VIT-AP · FFCS PLANNER · v1.0</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    status = data_status()
    visits = peek_visits()

    chips_html = "".join(
        f'<span class="ss-chip">{icon}{label}</span>'
        for label, icon in _CHIP_ICONS.items()
    )

    st.markdown(
        f"""
        <div class="ss-hero" data-testid="ss-hero">
          <span class="ss-hero-eyebrow"><span class="dot"></span>LIVE · REGISTRATION SEASON</span>
          <h1>Your perfect timetable,<br/><em>ready in minutes.</em></h1>
          <p class="lead">SlotSync is a calm, opinionated FFCS planner for VIT-AP.
          Search a course, pick a faculty, and watch a clean timetable appear —
          with instant clash detection and smart auto-generation.</p>
          <div class="ss-chips">{chips_html}</div>
          <div class="ss-stats" data-testid="ss-stats">
            <div class="ss-stat">
              <div class="label">Courses Loaded</div>
              <div class="value" data-testid="stat-courses">{status['num_courses']}</div>
              <div class="sub"></div>
            </div>
            <div class="ss-stat">
              <div class="label">Faculty Loaded</div>
              <div class="value" data-testid="stat-faculty">{status['num_faculty']}</div>
              <div class="sub"></div>
            </div>
            <div class="ss-stat">
              <div class="label">Students Helped</div>
              <div class="value" data-testid="stat-visits">{_fmt_count(visits)}</div>
              <div class="sub">persistent counter</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
