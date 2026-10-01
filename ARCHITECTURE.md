# Architecture

*System design only. For pipeline diagrams see `FLOW.md`, for build order see `PHASES.md`, for exact field/schema definitions see `PARAMETERS.md`.*

## 1. Tech Stack (locked)

| Layer | Technology |
|-------|-----------|
| UI / app | Python + Streamlit |
| Database | SQLite |
| Data processing | Pandas |
| PDF text extraction | PyMuPDF |
| OCR (scanned/image bills) | Tesseract OCR |
| Charts | Plotly |
| Classification | Rule-based (keyword matching), not ML |

Deliberately excluded from this stack: React, FastAPI, PostgreSQL, any ML classifier, chatbot layer, mobile app shell, or cloud infrastructure — see `ENHANCEMENTS.md`.

## 2. Folder Structure

```
carbon-footprint-estimator/
│
├── app.py                     # Main Streamlit application entrypoint
├── requirements.txt           # Python dependencies
├── README.md
│
├── frontend/                  # Streamlit UI pages
│   ├── upload.py              # Bill/invoice upload + verification forms
│   └── dashboard.py           # Analytics dashboard + "How was this calculated?"
│
├── backend/                   # Core processing logic
│   ├── calculator.py          # Activity & spend-based CO₂e calculation engine
│   ├── classifier.py          # Rule-based keyword → category mapper
│   ├── extractor.py           # PyMuPDF text & Tesseract OCR extraction
│   └── validators.py          # Input validation helpers
│
├── database/                  # SQLite database + schema
│   ├── carbon.db
│   └── db.py                  # All SQLite reads/writes, migrations, seeding
│
├── emission_factors/          # Reference emission factor data
│   ├── emission_factors.csv   # Cited factors with full metadata (15 fields)
│   └── category_rules.csv    # Keyword → category mapping rules
│
├── uploads/                   # User-uploaded bill/invoice files
│
├── sample_documents/          # Sample bills and invoices for testing
│   ├── electricity_bill.pdf
│   └── shopping_invoice.pdf
│
└── tests/                     # Test suite
    ├── test_calculator.py
    └── test_pipeline.py
```

## 3. Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `backend/extractor.py` | Check if a PDF has embedded text; extract it directly, or fall back to Tesseract OCR for images/scans; parse raw text into structured fields. OCR's only job is to read the document — it never calculates. |
| `backend/classifier.py` | Normalize product/vendor text, match against `category_rules.csv` keywords, fall back to "Other" if nothing matches |
| `backend/calculator.py` | `calculate_activity_emission()`, `calculate_spend_emission()` — the only place CO₂e math happens. Returns: activity_value, activity_unit, factor_value, factor_unit, result_co2e, method, source, version |
| `backend/validators.py` | Validate file types, required fields, and edge cases |
| `database/db.py` | All SQLite reads/writes for `users`, `documents`, `extracted_items`, `emission_factors`, `calculations` |
| `frontend/upload.py` | Bill/invoice upload UI + human verification form + result display |
| `frontend/dashboard.py` | Today/monthly totals, category breakdown, recent calculations, "How was this calculated?" per record |

## 4. Component Boundaries — Why They're Split This Way

- **Extraction is isolated from calculation.** OCR/PDF parsing only ever produces a *candidate* structured record; it never writes to the database directly or triggers calculation. This keeps a bad OCR read from silently corrupting footprint numbers.
- **Classification is isolated from calculation.** Category assignment is a lookup step, swappable later (e.g. for a smarter classifier) without touching the emission-factor math.
- **The calculation engine has no I/O.** `calculator.py` takes numbers in, returns numbers out — this is what makes it independently testable (see `PHASES.md` Phase 3).
- **The emission-factor table is data, not code.** Nothing in the backend hard-codes a factor value; every factor is looked up from `emission_factors/emission_factors.csv` / the `emission_factors` table. Factors are versioned rather than having one number hard-coded into the application.

## 5. Data Stores

Five SQLite tables back the whole app:

| Table | Purpose |
|-------|---------|
| `users` | Single local user for the prototype |
| `documents` | Uploaded bill/invoice file records |
| `extracted_items` | Structured data extracted from documents via OCR |
| `emission_factors` | Versioned emission factors with full source metadata (15 fields) |
| `calculations` | Every CO₂e calculation with full metadata (activity, factor, source, version, method, result) |

Full field-by-field definitions live in `PARAMETERS.md`.

## 6. Backend Endpoints (Logical)

The backend should handle these logical operations (implemented as Streamlit functions or future REST endpoints):

| Endpoint | Purpose |
|----------|---------|
| `/upload` | Accept bill/invoice file upload |
| `/extract` | Run OCR/text extraction on uploaded document |
| `/verify` | Accept user-verified/corrected extracted data |
| `/factors` | Look up emission factor for a given category |
| `/calculate` | Run CO₂e calculation using verified data + factor |
| `/records` | Retrieve saved calculation records |
| `/dashboard` | Aggregate totals (today, monthly, category breakdown) |

## 7. Single-User Assumption

The prototype assumes one local user and stores no credentials — no auth, OTP, or social login. This is a deliberate architectural simplification, not an oversight; multi-user support is listed in `ENHANCEMENTS.md` if the project ever needs it.
