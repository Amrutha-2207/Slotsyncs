# SlotSync

**The FFCS Planner VIT-AP students actually enjoy using.**

Build a clash-free timetable in 2–3 minutes. Search a course, pick a
faculty, add it, and watch a beautiful grid appear — with instant clash
detection and one-click auto-generation of every valid combination.

Designed like Linear. Built with Streamlit. Deployed on Streamlit Cloud.

<p align="center">
  <sub>Made with care for VIT-AP · CSV-driven · zero database</sub>
</p>

---

## ✨ Features

- **The 4-step flow** · Search → Choose Faculty → Add → Timetable
- **Smart clash detection** · atomic slot decomposition (`A1+TA1+TAA1`,
  `L37+L38`, compound cells like `TC1/G1`), physical minute-interval
  overlap checks that also catch theory ↔ lab collisions
- **Independent Theory + Lab selection** per course
- **Automatic timetable generator** — every valid faculty combination,
  clash-filtered, capped at 30 options
- **Day-Scholar vs Hosteller** modes (Day Scholar filters out anything
  starting before 09:00 or ending after 18:00)
- **PDF export** — landscape A4 with the timetable grid + course list
- **Persistent visitor counter** (survives Streamlit Cloud restarts,
  free service, no keys needed)
- **100% data-driven** — replace `data/courses.csv` and
  `data/faculty.csv` with the live registration data, push, and the app
  auto-updates with **zero code changes**

---

## 📅 Timetable model (VIT-AP official grid)

- 5 class days: **TUE, WED, THU, FRI, SAT**
- **Theory:** 10 hours/day (5 morning + 5 afternoon), 50-min bands
- **Lab:** 12 hours/day (6 morning + 6 afternoon), tighter bands
- Compound cells (e.g. `TC1/G1`, `TAA1/ECS`) are resolved to physical
  time intervals so any two courses picking either side clash correctly.

### Credit → slot patterns (validated in the app)

| Credits | Pattern            | Example       |
| ------: | ------------------ | ------------- |
| 4       | Lecture + T + TT   | `A1+TA1+TAA1` |
| 3       | Lecture + T        | `A1+TA1`      |
| 2       | Lecture only       | `A1`          |
| 1       | Tutorial only      | `TA1`         |

Lab credits are counted separately via the `Lab` component in
`faculty.csv`.

---

## 🗂 Data format

### `data/courses.csv`

```csv
Course Code,Course Name,Credits,Course Type
CSE2001,Data Structures and Algorithms,4,Theory+Lab
CSE2002,Artificial Intelligence,4,Theory
MAT2001,Discrete Mathematical Structures,4,Theory
STS1001,Qualitative and Quantitative Skills Practice I (STS),1,Theory
```

- `Course Type` = `Theory`, `Lab` or `Theory+Lab`.

### `data/faculty.csv`

```csv
CourseCode,CourseName,Component,FacultyName,Slot
CSE2001,Data Structures and Algorithms,Theory,Deepashika Mishra,A1+TA1+TAA1
CSE2001,Data Structures and Algorithms,Lab,Deepashika Mishra,L37+L38
```

- `CourseCode` must match a row in `courses.csv` — this is how the app
  joins offerings to courses.
- `Component` = `Theory` or `Lab`.
- `Slot` is the compound FFCS slot code joined by `+`.

The app is **tolerant of the older schema** (`Course, Component,
Faculty, Slot`) — it back-fills `CourseCode` from `CourseName`
automatically.

---

## 🚀 Run locally

```bash
git clone https://github.com/Amrutha-2207/SlotSync.git
cd SlotSync
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repo to GitHub (or use the **Save to GitHub** button in
   Emergent).
2. Go to <https://share.streamlit.io/> → **New app**.
3. Point to `Amrutha-2207/SlotSync`, branch `main`, main file `app.py`.
4. Click **Deploy**. Done — `.streamlit/config.toml` and
   `requirements.txt` are already tuned for Community Cloud.

### Updating course/faculty data after deployment

You only need to change the CSVs — no code edits required:

```bash
# Edit or replace data/faculty.csv and data/courses.csv
git add data/*.csv
git commit -m "Update faculty offerings"
git push
```

Streamlit Cloud will re-deploy automatically within a few seconds and
the app will pick up the new data.

---

## 🧩 Project structure

```
.
├── app.py                        # single-page entry (tabs, sidebar)
├── requirements.txt
├── .streamlit/
│   └── config.toml               # theme + server settings
├── data/
│   ├── courses.csv
│   └── faculty.csv
├── components/
│   ├── hero.py                   # hero, stats, feature chips
│   ├── search.py                 # search box + course card + faculty pickers
│   ├── selected.py               # selected list with credits + edit/delete
│   ├── timetable_view.py         # rendered timetable + legend
│   ├── generator.py              # Option 01..N with Apply
│   └── export.py                 # PDF download
└── utils/
    ├── slots.py                  # canonical VIT-AP grid (Tue–Sat)
    ├── clash.py                  # interval-based clash detection
    ├── data.py                   # CSV loaders (tolerant, cached)
    ├── timetable.py              # HTML grid renderer + colour map
    ├── generator.py              # cartesian generator + day-scholar filter
    ├── counter.py                # visitor counter (abacus.jasoncameron.dev)
    ├── export.py                 # ReportLab PDF exporter
    └── style.py                  # global CSS (Instrument Serif + Geist)
```

Everything is small, focused, and testable.

---

## 🧪 How clash detection works

Each slot atom (e.g. `A1`, `TC1`, `L37`) is mapped to a list of
**physical (day, start_min, end_min)** intervals from the VIT-AP grid
in `utils/slots.py`. Two courses clash when **any** of their intervals
overlap in real time — regardless of whether the atoms share a name.

Concrete examples the app handles correctly:

| Case                                    | Result       | Why                                    |
| --------------------------------------- | ------------ | -------------------------------------- |
| `TC1` vs `G1`                           | ⚠ Clash      | Same physical cell TUE 11:00–11:50     |
| `A1` (theory) vs `L2` (lab)             | ⚠ Clash      | TUE 09:00–09:50 overlaps 08:50–09:40   |
| `A1+TA1+TAA1` vs `A1+TA1+TAA1`          | ⚠ Clash      | Identical atoms                        |
| `A1+TA1+TAA1` vs `L37+L38`              | ✓ Fine       | WED 15:00–16:40 vs AI theory on TUE/FRI |
| Day Scholar mode + `E2+TE2+TEE2`        | Removed      | TEE2 ends 18:50 (> 18:00)              |

---

## 🎨 Design notes

- Typography: **Instrument Serif** (display) + **Geist** (UI) +
  **Geist Mono** (metadata) — deliberately avoiding Inter/Roboto/Arial.
- Palette: soft neutrals, cell-tinted timetable cards. Light-first,
  dark-mode friendly through CSS variables.
- Every interactive element carries a stable `data-testid`.

---

## 🧰 Development workflow

Run the linters:

```bash
pip install ruff
ruff check .
```

Push to `main` — Streamlit Cloud redeploys automatically.

---
## 🤖 Development Transparency

This project was built using modern AI-assisted development tools:

- **Emergent AI** — Used for scaffolding the initial project structure, generating boilerplate code, and rapid prototyping during the 14-hour build sprint
- **ChatGPT** — Debugging partner for fixing the slot clash detection algorithm and CSS layout issues
- **Google AI Studio (Gemini)** — Testing the data pipeline and validating faculty CSV parsing logic

**What I personally wrote/designed:**
- ✅ The entire clash detection algorithm logic (`utils/clash.py`) — interval-based overlap checking that handles compound slots like TC1/G1
- ✅ Data schema design for `courses.csv` and `faculty.csv` (atomic slot decomposition, credit validation)
- ✅ Timetable generation algorithm (`utils/generator.py`) — cartesian product of faculty combinations with day-scholar filtering
- ✅ UI/UX design decisions (Instrument Serif typography, soft color palette, 4-step flow)
- ✅ Deployment architecture (Streamlit Cloud + persistent visitor counter integration)

**What AI helped accelerate:**
- ⚡ Initial Streamlit boilerplate and component structure
- ⚡ CSS styling for the timetable grid (I designed it, AI wrote the CSS)
- ⚡ ReportLab PDF export code (I specified the layout, AI implemented it)
- ⚡ Handling edge cases in CSV parsing (tolerant schema with back-fill logic)

**Code Ownership Proof:**
- I can explain every function in this codebase without looking at the code
- [Link to detailed architecture walkthrough] 
- [Link to demo video where I explain the clash detection algorithm] 

This is the reality of modern software engineering in 2026 — AI tools are productivity multipliers, not replacements for engineering judgment. The hard parts (algorithm design, data modeling, deployment debugging) still require human expertise.

If you're a recruiter or interviewer reading this: I'm happy to do a live code review session where I explain any part of this codebase in depth. Transparency > hiding tool usage.

## ❤️ Credits

Built for VIT-AP by Amrutha . Feedback and pull
requests welcome.
