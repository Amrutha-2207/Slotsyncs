# PRD — SlotSync

**A smart FFCS Planner for VIT-AP · pure Streamlit · deploys to Streamlit Community Cloud.**

## Original Problem Statement

Build the best FFCS Planner VIT-AP students have ever used. Apple minimalism,
Linear polish, Stripe production quality. A student picks a timetable in
2–3 minutes. Pure Streamlit + Pandas, CSV-driven, no DB. Deployed on
Streamlit Community Cloud.

**Iteration 2 refactor** (2026-01-04, evening):
- Real VIT-AP timetable grid (Tue–Sat, 10 theory hrs + 12 lab hrs/day,
  compound cells like `TC1/G1`).
- Six real courses (DSA, AI, CAO, DMS, STS, Entrepreneurship).
- New faculty.csv schema `CourseCode,CourseName,Component,FacultyName,Slot`.
- Credit → slot pattern mapping (4cr = `A1+TA1+TAA1`, 3cr = `A1+TA1`,
  2cr = `A1`, 1cr = `TA1`).
- Interval-based clash detection (catches compound-cell aliasing and
  theory ↔ lab time overlaps).

---

## User Personas

- **The Registration-Day Student** — needs a clash-free timetable under
  pressure, on wobbly campus Wi-Fi.
- **The Day Scholar** — wants options that fit around a commute (no
  8:00 AM classes, no 6:30 PM classes).
- **The Optimiser** — wants to see every valid faculty combination
  side-by-side.

---

## Core Requirements (static)

- Fully data-driven from `data/courses.csv` + `data/faculty.csv`.
- Slot-atom decomposition + interval overlap for compound cells.
- Independent Theory + Lab per course.
- Automatic timetable generator (cartesian × clash-filter).
- Day-Scholar vs Hosteller modes.
- PDF export.
- Persistent visitor counter surviving Streamlit Cloud restarts.

---

## What's implemented (2026-01-04, iteration 2)

### Data / core logic
- `utils/slots.py` — canonical VIT-AP grid (Tue–Sat) with THEORY_GRID
  (10 hrs × 5 days), LAB_GRID (12 hrs × 5 days), and
  `SLOT_TO_INTERVALS` resolving compound cells to physical minute-bands.
- `utils/clash.py` — physical-interval overlap detection
  (`clashes_with`, `combo_clash`, `has_internal_clash`).
- `utils/data.py` — tolerant CSV loading with new schema + legacy
  fallback (auto-backfills `CourseCode` from `CourseName`).
- `utils/generator.py` — cartesian generator using `course_code`; Day
  Scholar filter in minutes.
- `utils/counter.py` — abacus.jasoncameron.dev counter + local fallback.
- `utils/export.py` — landscape A4 PDF with the Tue–Sat grid + course
  list.
- `utils/timetable.py` — HTML grid renderer, 5 days × 2 rows each,
  compound cells resolved via atom membership.
- `utils/style.py` — Instrument Serif + Geist typography; tightened
  timetable CSS for the denser lab row.

### UI components
- `components/hero.py`, `search.py`, `selected.py`,
  `timetable_view.py`, `generator.py`, `export.py` — all wired to the
  new `CourseCode`-based API. Search fixed IndexError on Theory+Lab
  courses with empty lab data.

### App shell
- `app.py`, `.streamlit/config.toml`, `requirements.txt`, `.gitignore`,
  comprehensive `README.md` with data schema, credit mapping table,
  deployment instructions, and clash-detection cheatsheet.

### Data
- `data/courses.csv` — 6 courses:
  - CSE2001 DSA 4 cr Theory+Lab
  - CSE2002 AI 4 cr Theory
  - CSE2003 CAO 4 cr Theory+Lab
  - MAT2001 DMS 4 cr Theory
  - STS1001 STS 1 cr Theory
  - MGT2001 Entrepreneurship 4 cr Theory
- `data/faculty.csv` — 25 offerings, 19 unique placeholder faculty,
  new `CourseCode,CourseName,Component,FacultyName,Slot` schema.
  User will overwrite with real registration data post-live.

### Testing status
- E2E frontend (Playwright) — iteration 1 pre-refactor 100%.
- E2E frontend iteration 2 (post-refactor) — **100 % pass** on all 16
  flows (hero, search, expander, dropdowns, compound-cell clash,
  interval clash, timetable Tue–Sat render, generator, Day Scholar,
  Apply, PDF export, selected/edit/delete, robustness).
- Self-review: no lint errors, all sanity assertions pass, PDF
  produces valid `%PDF`.

---

## Backlog / P1 (post-launch polish)

- **P1** — Live-as-you-type search (bypass Streamlit's Enter/blur
  commit) with debounce.
- **P1** — Highlight overlapping courses inside the timetable cell
  itself when the user overrides a warned clash.
- **P2** — Shareable-timetable URL (encode selection in query params).
- **P2** — Save/load timetable JSON to browser localStorage.
- **P2** — Optional dark-mode CSS variant.

---

## Deployment

**Local:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Streamlit Community Cloud:**
1. Save to GitHub (Emergent chat input) → repo `Amrutha-2207/SlotSync`.
2. share.streamlit.io → New app → point to `app.py`.
3. Deploy. `.streamlit/config.toml` + `requirements.txt` are pre-tuned.

**Updating data post-deploy:** just edit the two CSVs, commit, push.
Streamlit Cloud redeploys automatically.

---

## Next Action Items

1. **Push to GitHub** using the "Save to GitHub" button in the Emergent
   chat input — this will publish the code to
   `https://github.com/Amrutha-2207/SlotSync`.
2. Deploy on Streamlit Community Cloud (see README).
3. Once registration data arrives, replace `data/faculty.csv` (same
   schema) — no code changes needed.
4. Optional polish: P1 items above.
