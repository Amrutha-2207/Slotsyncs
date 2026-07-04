# SlotSync

**A smart FFCS Planner for VIT-AP — built for calm, fast timetable building.**

Search a course, pick a faculty, add it, and watch a clean timetable appear —
with instant clash detection and one-click auto-generation of every valid
combination. Designed to feel like Linear. Built to be deployed today.

---

## ✨ Features

- **4-step flow**: Search → Choose Faculty → Add Course → View Timetable
- **Smart clash detection**: atomic slot decomposition (splits `A1+TA1+TAA1`,
  `L37+L38`, etc.), cell-level overlap check, inline warnings that name the
  conflicting course
- **Independent Theory + Lab selection** per course
- **Automatic timetable generator**: cartesian product of every faculty
  combination, filtered by clashes
- **Day-Scholar vs Hosteller** mode toggle (Day Scholar removes any option
  with a class before 9:00 AM or after 6:00 PM)
- **PDF export** of the final timetable and course list (landscape A4)
- **Persistent visitor counter** (`abacus.jasoncameron.dev` with local fallback)
- **100% data-driven** — everything is read from `data/courses.csv` and
  `data/faculty.csv`; no code changes needed to update data

---

## 📁 Project Structure

```
.
├── app.py                     # single-page entry (tabs)
├── requirements.txt
├── .streamlit/config.toml     # theme + server settings for Streamlit Cloud
├── data/
│   ├── courses.csv            # Course Code, Course Name, Credits, Course Type
│   └── faculty.csv            # Course, Component, Faculty, Slot
├── components/
│   ├── hero.py                # hero + stats
│   ├── search.py              # search + course card + faculty selection
│   ├── selected.py            # selected-courses list with edit/delete
│   ├── timetable_view.py      # timetable grid renderer
│   ├── generator.py           # auto-generator UI
│   └── export.py              # PDF export UI
└── utils/
    ├── slots.py               # VIT-AP FFCS slot grid (canonical)
    ├── clash.py               # slot-atom decomposition + clash checks
    ├── data.py                # CSV loading (cached, tolerant)
    ├── timetable.py           # grid builder + HTML renderer
    ├── generator.py           # combination generator (+ Day-Scholar filter)
    ├── counter.py             # persistent visitor counter
    ├── export.py              # reportlab PDF exporter
    └── style.py               # global CSS (Apple/Linear inspired)
```

---

## 🗂 Data format

### `data/courses.csv`

| Course Code | Course Name              | Credits | Course Type   |
| ----------- | ------------------------ | ------- | ------------- |
| CSE2001     | Data Structures & Algos  | 4       | Theory+Lab    |
| MAT1001     | Calculus                 | 4       | Theory        |

`Course Type` accepts `Theory`, `Lab` or `Theory+Lab`.

### `data/faculty.csv`

| Course                   | Component | Faculty            | Slot        |
| ------------------------ | --------- | ------------------ | ----------- |
| Artificial Intelligence  | Theory    | Monali Bordoloi    | A1+TA1      |
| Data Structures & Algos  | Lab       | Deepashika Mishra  | L37+L38     |

`Course` must match `Course Name` exactly from `courses.csv`.
`Component` is `Theory` or `Lab`. `Slot` follows the VIT-AP FFCS format
(compound slots joined by `+`).

You can safely overwrite these files with your live registration data —
the app is fully data-driven and re-loads on save.

---

## 🚀 Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) → **New app**.
3. Point to the repo, branch `main`, and set the main file to `app.py`.
4. Click **Deploy**. That's it — `.streamlit/config.toml` and
   `requirements.txt` are already tuned for Community Cloud.

**Visitor counter**: The counter uses the free public
[abacus.jasoncameron.dev](https://abacus.jasoncameron.dev) service and needs
no keys. To reset the counter or use your own namespace, edit
`_NAMESPACE` / `_KEY` at the top of `utils/counter.py`.

---

## 🎨 Design notes

- Typography: **Instrument Serif** (display) + **Geist** (UI) + **Geist Mono**
  (metadata) — a deliberate escape from the Inter/Roboto default.
- Palette: soft neutrals with cell-tinted timetable cards; no harsh colours.
- Every interactive element carries a `data-testid` for reliable testing.

Made with care for VIT-AP students.
