# PRD — SlotSync

**A smart FFCS Planner for VIT-AP · pure Streamlit · deploys to Streamlit Community Cloud.**

## Original Problem Statement

Continue the existing minimal Streamlit repo at
`github.com/Amrutha-2207/SlotSync` and turn it into the BEST FFCS Planner
VIT-AP students have ever used. Think Apple. Design like Linear. Build like
Stripe. Minimal, elegant, and effortless — a student should build a complete
timetable in 2–3 minutes.

Four-step flow: **Search → Choose Faculty → Add Course → View Timetable**.
Tech stack: Python + Streamlit + Pandas + Session State + CSV data. No DB.
Persistent visitor counter that survives Streamlit Cloud restarts.

---

## User Personas

- **The Registration-Day Student** — needs to build a clash-free timetable
  under time pressure, on wobbly campus Wi-Fi.
- **The Day Scholar** — wants only morning/afternoon options that fit
  around a commute (no early or evening classes).
- **The Optimiser** — wants to see every valid faculty combination and
  compare them side-by-side.

---

## Core Requirements (static)

- Fully data-driven from `data/courses.csv` and `data/faculty.csv`.
- Slot-atom decomposition (`A1+TA1+TAA1`, `L37+L38`) with cell-level
  overlap detection.
- Theory and Lab picked independently per course.
- Automatic timetable generator (cartesian product, clash-filtered).
- PDF export of the finalised timetable + course list.
- Persistent visitor counter that survives redeploys.
- Streamlit Community Cloud deployable out of the box.

---

## What's implemented (2026-01-04)

### Data / core logic
- `utils/slots.py` — canonical VIT-AP FFCS grid (5 days × 12 bands, theory
  + lab lanes), atom splitter, cell-mapping helpers.
- `utils/clash.py` — cell-based clash detection, internal (theory↔lab)
  overlap, combo-level clash for the generator.
- `utils/data.py` — cached CSV loading with tolerant column normalisation.
- `utils/generator.py` — cartesian product of every faculty combination
  with Day-Scholar filter and configurable max-options cap.
- `utils/counter.py` — persistent visitor counter via
  `abacus.jasoncameron.dev` with local JSON fallback.
- `utils/export.py` — landscape A4 PDF via ReportLab with course list.
- `utils/style.py` — Apple/Linear-inspired CSS (Instrument Serif + Geist).
- `utils/timetable.py` — grid builder + HTML renderer with soft palette.

### UI components (tabs on a single page)
- `components/hero.py` — hero, six feature chips, three stat cards
  (Courses / Faculty / Students Helped).
- `components/search.py` — search box, course expander cards, Theory + Lab
  dropdowns with per-option clash indicator (🟢 / 🟠), Add/Update button.
- `components/selected.py` — selected list with credits summary and edit /
  delete controls.
- `components/timetable_view.py` — beautiful 5-day timetable with colour
  legend.
- `components/generator.py` — Option 01/02/…, per-option preview + Apply.
- `components/export.py` — Download PDF button.

### App shell
- `app.py` — page config, sidebar (Hosteller / Day Scholar radio, session
  summary, Clear All), tabs, footer.
- `.streamlit/config.toml` — theme + server settings for Streamlit Cloud.
- `requirements.txt`, `.gitignore`, `README.md` — deployment-ready.
- Sample data with 15 courses + 48 faculty offerings (real VIT-AP style
  slots) for immediate use; user will overwrite with live registration data.

### Testing status
- E2E frontend testing (Playwright) — **100 % pass** on all 13 flows:
  hero, search filter, expander open, Theory/Lab dropdowns, clash detection,
  add/update, selected panel, timetable render, auto-generator, day-scholar
  filter, sidebar toggle, PDF export, error resilience.

---

## Backlog / P1 (post-launch polish)

- **P1** — Add a subtle "overlapping course" warning in the timetable cell
  itself when the user overrides a flagged clash.
- **P1** — Live-as-you-type search (bypass Streamlit's Enter/blur commit)
  with a small debounce via a `st.text_input` callback.
- **P2** — Per-slot preference weighting in the generator (e.g. "prefer
  morning" / "avoid Wednesday").
- **P2** — Save/load timetable JSON to browser localStorage so a student
  can return later without repicking.
- **P2** — Optional dark-mode CSS variant.

---

## Deployment

**Local:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Streamlit Community Cloud:** push to GitHub → New App → point to
`app.py`. Nothing else to configure — `.streamlit/config.toml` and
`requirements.txt` are already tuned.

---

## Next Action Items

1. Overwrite `data/courses.csv` and `data/faculty.csv` with the real
   post-registration data (schema unchanged).
2. Deploy to Streamlit Community Cloud from the SlotSync repo.
3. (Optional polish) implement the P1 items above.
