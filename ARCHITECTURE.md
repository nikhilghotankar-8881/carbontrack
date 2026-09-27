# Architecture

*System design only. For pipeline diagrams see `FLOW.md`, for build order see `PHASES.md`, for exact field/schema definitions see `PARAMETERS.md`.*

## 1. Tech stack (locked)

| Layer | Technology |
|---|---|
| UI / app | Python + Streamlit |
| Database | SQLite |
| Data processing | Pandas |
| PDF text extraction | PyMuPDF |
| OCR (scanned/image bills) | Tesseract OCR |
| Charts | Plotly |
| Classification | Rule-based (keyword matching), not ML |

Deliberately excluded from this stack: React, FastAPI, PostgreSQL, any ML classifier, chatbot layer, mobile app shell, or cloud infrastructure — see `ENHANCEMENTS.md`.

## 2. Folder structure

```
carbon-footprint-estimator/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── emission_factors.csv
│   └── category_rules.csv
│
├── database/
│   └── carbon.db
│
├── modules/
│   ├── database.py
│   ├── calculator.py
│   ├── classifier.py
│   ├── extractor.py
│   ├── recommendations.py
│   └── validators.py
│
├── pages/
│   ├── dashboard.py
│   ├── upload.py
│   ├── purchases.py
│   └── history.py
│
└── sample_data/
    ├── bills/
    └── purchases.csv
```

## 3. Module responsibilities

| Module | Responsibility |
|---|---|
| `modules/validators.py` | Validate CSV columns, required fields, file types before anything else runs |
| `modules/extractor.py` | Check if a PDF has embedded text; extract it directly, or fall back to Tesseract OCR for images/scans; parse raw text into structured fields |
| `modules/classifier.py` | Normalize product/vendor text, match against `category_rules.csv` keywords, fall back to "Other" if nothing matches |
| `modules/calculator.py` | `calculate_activity_emission()`, `calculate_spend_emission()`, `calculate_total_emission()` — the only place CO₂e math happens |
| `modules/database.py` | All SQLite reads/writes for `transactions` and `emission_factors` |
| `modules/recommendations.py` | Rule-based lookup: highest category → matching suggestion string |
| `pages/upload.py` | Bill/receipt upload UI + extracted-field verification form |
| `pages/purchases.py` | CSV upload, preview table, confirm-import step |
| `pages/dashboard.py` | KPI cards, category/daily/monthly Plotly charts, recommendation panel |
| `pages/history.py` | Transaction table with view/edit/delete |

## 4. Component boundaries — why they're split this way

- **Extraction is isolated from calculation.** OCR/PDF parsing only ever produces a *candidate* structured record; it never writes to the database directly. This keeps a bad OCR read from silently corrupting footprint numbers.
- **Classification is isolated from calculation.** Category assignment is a lookup step, swappable later (e.g. for a smarter classifier) without touching the emission-factor math.
- **The calculation engine has no I/O.** `calculator.py` takes numbers in, returns numbers out — this is what makes it independently testable (see `PHASES.md` Phase 3).
- **The emission-factor table is data, not code.** Nothing in `modules/` hard-codes a factor value; every factor is looked up from `data/emission_factors.csv` / the `emission_factors` table.

## 5. Data stores

Three SQLite tables back the whole app: `transactions`, `emission_factors`, `users` (single local user). Full field-by-field definitions live in `PARAMETERS.md`.

## 6. Single-user assumption

The prototype assumes one local user and stores no credentials — no auth, OTP, or social login. This is a deliberate architectural simplification, not an oversight; multi-user support is listed in `ENHANCEMENTS.md` if the project ever needs it.
