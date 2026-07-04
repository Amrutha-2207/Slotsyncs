"""Global CSS + design tokens for SlotSync — Apple/Linear inspired."""
import streamlit as st


CSS = """
<style>
/* ---- fonts ---- */
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap');

:root {
  --ink: #0F172A;
  --ink-2: #334155;
  --muted: #64748B;
  --line: #E5E7EB;
  --line-2: #F1F5F9;
  --bg: #FAFAF7;
  --surface: #FFFFFF;
  --accent: #0F172A;
  --accent-soft: #F1F5F9;
  --good: #16A34A;
  --warn: #D97706;
  --danger: #DC2626;
  --shadow: 0 1px 2px rgba(15,23,42,.04), 0 8px 24px -12px rgba(15,23,42,.08);
  --radius: 18px;
}

html, body, [class*="css"]  {
  font-family: 'Geist', ui-sans-serif, system-ui, -apple-system, sans-serif !important;
  color: var(--ink);
}

.stApp { background: var(--bg) !important; }

/* Hide default streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

/* Layout */
.block-container { padding-top: 1.2rem !important; max-width: 1180px; }

/* ---------- Nav Bar ---------- */
.ss-nav {
  display:flex; align-items:center; justify-content:space-between;
  padding: 10px 4px; margin-bottom: 8px;
}
.ss-brand {
  display:flex; align-items:center; gap:10px;
  font-weight: 600; font-size: 18px; letter-spacing: -0.01em;
}
.ss-brand-mark {
  width: 26px; height: 26px; border-radius: 8px;
  background: linear-gradient(135deg, #0F172A 0%, #334155 100%);
  display:inline-flex; align-items:center; justify-content:center; color:white;
  font-family: 'Geist Mono', monospace; font-size: 13px;
}
.ss-nav-meta {
  font-family: 'Geist Mono', monospace;
  color: var(--muted); font-size: 12px; letter-spacing: 0.02em;
}

/* ---------- Hero ---------- */
.ss-hero { padding: 42px 0 24px; }
.ss-hero-eyebrow {
  display:inline-flex; align-items:center; gap:8px;
  font-family: 'Geist Mono', monospace; font-size: 11px;
  letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--muted); padding: 6px 10px;
  border: 1px solid var(--line); border-radius: 999px;
  background: var(--surface);
}
.ss-hero-eyebrow .dot {
  width:6px; height:6px; border-radius:50%; background:#16A34A;
  box-shadow: 0 0 0 3px rgba(22,163,74,.15);
}
.ss-hero h1 {
  font-family: 'Instrument Serif', 'Geist', serif;
  font-weight: 400; font-size: 72px; line-height: 1.02;
  letter-spacing: -0.02em; margin: 18px 0 8px;
  color: var(--ink);
}
.ss-hero h1 em {
  font-style: italic; color: #334155;
}
.ss-hero p.lead {
  font-size: 18px; color: var(--ink-2); max-width: 640px;
  line-height: 1.55; margin: 8px 0 22px;
}

/* Feature chips */
.ss-chips { display:flex; flex-wrap:wrap; gap:8px; margin: 16px 0 8px; }
.ss-chip {
  font-size: 13px; color: var(--ink-2);
  padding: 8px 12px; border: 1px solid var(--line); border-radius: 999px;
  background: var(--surface); display:inline-flex; align-items:center; gap:6px;
}
.ss-chip svg { width:14px; height:14px; }

/* Stats */
.ss-stats {
  display:grid; grid-template-columns: repeat(3, 1fr);
  gap: 14px; margin-top: 26px;
}
.ss-stat {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow);
}
.ss-stat .label {
  font-family: 'Geist Mono', monospace; font-size: 11px;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted);
}
.ss-stat .value {
  font-family: 'Instrument Serif', serif; font-weight:400;
  font-size: 40px; line-height: 1; color: var(--ink); margin-top:8px;
  letter-spacing: -0.02em;
}
.ss-stat .sub { color: var(--muted); font-size: 12px; margin-top: 6px; }

/* Section titles */
.ss-section-title {
  display:flex; align-items:baseline; justify-content:space-between; gap:12px;
  margin: 28px 0 12px;
}
.ss-section-title h2 {
  font-family: 'Instrument Serif', serif; font-weight: 400;
  font-size: 30px; letter-spacing: -0.01em; margin: 0; color: var(--ink);
}
.ss-section-title .aside {
  font-family: 'Geist Mono', monospace; font-size: 11px;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted);
}

/* Cards & panels */
.ss-panel {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow);
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] > div {
  border-radius: 12px !important;
  border-color: var(--line) !important;
  background: var(--surface) !important;
}
[data-testid="stTextInput"] input {
  padding: 12px 14px !important; font-size: 15px !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--ink) !important;
  box-shadow: 0 0 0 3px rgba(15,23,42,.06) !important;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
  border-radius: 12px !important;
  border: 1px solid var(--line) !important;
  background: var(--surface) !important;
  color: var(--ink) !important;
  font-weight: 500 !important;
  padding: 8px 16px !important;
  transition: transform .12s ease, background .18s ease, box-shadow .18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  background: var(--accent-soft) !important;
  transform: translateY(-1px);
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
  background: var(--ink) !important; color: white !important;
  border-color: var(--ink) !important;
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
  background: #1E293B !important;
  box-shadow: 0 6px 20px -8px rgba(15,23,42,.35);
}

/* Course card */
.ss-course {
  background: var(--surface); border:1px solid var(--line);
  border-radius: var(--radius); padding: 16px 18px; margin-bottom: 10px;
  transition: border-color .18s ease, transform .12s ease;
}
.ss-course:hover { border-color: #CBD5E1; }
.ss-course-head { display:flex; justify-content:space-between; align-items:center; gap:12px; }
.ss-course-title { font-size:16px; font-weight:600; letter-spacing:-0.01em; }
.ss-course-meta {
  font-family:'Geist Mono', monospace; color: var(--muted); font-size:12px;
  display:flex; gap:10px; align-items:center;
}
.ss-course-badge {
  font-family:'Geist Mono', monospace; font-size:11px; letter-spacing:.1em;
  padding: 3px 8px; border-radius: 999px; border:1px solid var(--line);
  color: var(--ink-2); background: var(--accent-soft);
}

/* Selected course pill */
.ss-selected {
    background: var(--surface); border:1px solid var(--line);
    border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;
    display:flex; justify-content: space-between; align-items:center; gap:14px;
    overflow: visible !important;
    position: relative !important;
    z-index: 9999 !important;
}
.ss-selected .left { min-width:0; }
.ss-selected .code {
    font-family: 'Geist Mono', monospace; font-size:11px; letter-spacing:.14em;
    color: var(--muted); text-transform: uppercase;
}
.ss-selected .name {
    font-size:15px; font-weight:600; letter-spacing:-0.01em; margin-top:2px;
    overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
.ss-selected .meta {
    font-size:12px; color: var(--ink-2); margin-top:4px;
    display:flex; flex-wrap:wrap; gap:8px;
}
.ss-selected .meta span {
    padding: 2px 8px; border:1px solid var(--line); border-radius:999px;
    background: var(--accent-soft);
    font-family: 'Geist Mono', monospace; font-size:11px;
}

/* Clash callout */
.ss-clash {
  border:1px solid #FED7AA; background: #FFF7ED;
  color:#9A3412; padding: 12px 14px; border-radius: 12px;
  font-size: 13px; margin: 8px 0;
  display:flex; gap:10px; align-items:flex-start;
}
.ss-clash .icn { color: #EA580C; margin-top:1px; }

.ss-ok {
  border:1px solid #BBF7D0; background: #F0FDF4;
  color:#166534; padding: 10px 14px; border-radius: 12px;
  font-size: 13px; margin: 8px 0;
}

/* Slot pill in select-option */
.slot-pill-ok { color:#16A34A; }
.slot-pill-clash { color:#EA580C; }

/* Timetable */
.tt-wrap { overflow-x: auto; border:1px solid var(--line); border-radius: var(--radius); background: var(--surface); box-shadow: var(--shadow); }
.tt { width:100%; border-collapse: separate; border-spacing: 0; table-layout: fixed; }
.tt th, .tt td {
  border-right: 1px solid var(--line-2);
  border-bottom: 1px solid var(--line-2);
  vertical-align: middle;
}
.tt th:last-child, .tt td:last-child { border-right: none; }
.tt tr:last-child td { border-bottom: none; }
.tt-th, .tt-th-sub {
  padding: 8px 4px; font-weight: 500; font-size: 10px;
  letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted);
  background: var(--bg); text-align: center;
}
.tt-th { font-size: 11px; font-weight: 600; color: var(--ink-2); }
.tt-th-day { text-align: left; padding: 10px 12px; width: 90px; }
.tt-th-sub { font-size: 9px; padding: 6px 3px; font-family: 'Geist Mono', monospace; text-transform: none; letter-spacing: 0.02em; line-height: 1.25; color: var(--muted); background: #F8FAFC; }
.tt-sub-empty { color: #CBD5E1; }
.tt-day {
  background: var(--bg);
  padding: 8px 12px;
  text-align: left;
  min-width: 90px;
}
.tt-day-name {
  font-weight: 600; font-size: 12px; color: var(--ink); letter-spacing: -0.01em;
}
.tt-day-lane {
  font-family: 'Geist Mono', monospace; font-size: 9px;
  letter-spacing: 0.14em; color: var(--muted); margin-top: 2px;
}
.tt-day-lab { border-top: 1px dashed var(--line-2); }
.tt-cell {
  height: 56px; padding: 5px 6px; text-align: center; position: relative;
  font-family: 'Geist Mono', monospace;
}
.tt-cell-empty { background: var(--surface); }
.tt-cell-gap { background: repeating-linear-gradient(45deg, transparent 0 4px, #F8FAFC 4px 8px); }
.tt-cell-hint {
  font-size: 9px; color: #CBD5E1; letter-spacing: 0.04em;
  font-family: 'Geist Mono', monospace;
}
.tt-filled { }
.tt-code { font-weight: 700; font-size: 11px; letter-spacing: -0.01em; color: var(--ink); font-family: 'Geist', sans-serif; }
.tt-fac  { font-size: 9px; color: var(--ink-2); margin-top: 1px;
           white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
           font-family: 'Geist', sans-serif; }
.tt-slot { font-family: 'Geist Mono', monospace; font-size: 9px;
           color: var(--muted); margin-top: 2px; letter-spacing: 0.02em; }
.tt-tag  { display: inline-block; padding: 0 4px; border-radius: 3px;
           background: rgba(15,23,42,.14); color: var(--ink); margin-right: 4px;
           font-weight: 700; font-size: 8px; }
.tt-tag-lab { background: rgba(15,23,42,.08); }
.tt-day-lab-row td { background: #FCFCFA; }

/* Divider */
.ss-hr { height:1px; background: var(--line); margin: 22px 0; border:0; }

/* Small helpers */
.ss-mute { color: var(--muted); }
.ss-mono { font-family: 'Geist Mono', monospace; }

/* Tabs */
[data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); }
[data-baseweb="tab"] {
  background: transparent !important; border-radius: 10px 10px 0 0 !important;
  padding: 10px 14px !important; color: var(--muted) !important;
  font-weight: 500 !important;
}
[data-baseweb="tab"][aria-selected="true"] {
  color: var(--ink) !important; background: var(--surface) !important;
  border: 1px solid var(--line) !important; border-bottom-color: var(--surface) !important;
}

/* Expander */
[data-testid="stExpander"] {
  border: 1px solid var(--line) !important; border-radius: var(--radius) !important;
  background: var(--surface) !important; box-shadow: var(--shadow); margin-bottom: 10px;
}
[data-testid="stExpander"] summary {
  padding: 14px 18px !important;
  font-weight: 500 !important;
  color: var(--ink) !important;
}
[data-testid="stExpander"] svg { color: var(--muted); }

/* Info banners */
[data-testid="stAlert"] { border-radius: 14px !important; border: 1px solid var(--line) !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] .block-container { padding-top: 1rem !important; }

/* Toggle spacing */
[data-testid="stToggle"] label p { color: var(--ink); font-weight: 500; }

/* Option card in generator */
.ss-option-card {
  background: var(--surface); border:1px solid var(--line);
  border-radius: var(--radius); padding: 16px 18px; margin-bottom: 12px;
  box-shadow: var(--shadow);
}
.ss-option-head {
  display:flex; justify-content: space-between; align-items:center;
  margin-bottom: 8px;
}
.ss-option-num {
  font-family:'Instrument Serif', serif; font-size: 28px;
  color: var(--ink); letter-spacing: -0.02em;
}
.ss-option-meta {
  font-family:'Geist Mono', monospace; font-size:11px;
  letter-spacing: .14em; text-transform: uppercase; color: var(--muted);
}
.ss-option-body ul { margin:0; padding-left: 18px; }
.ss-option-body li { font-size: 13px; color: var(--ink-2); margin: 3px 0; }

/* Footer */
.ss-foot {
  color: var(--muted); font-size: 12px; text-align:center;
  padding: 32px 0 16px; font-family: 'Geist Mono', monospace;
  letter-spacing: 0.06em;
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
