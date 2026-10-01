# 🌱 CarbonTrack — Personal Carbon Footprint Estimator

**CarbonTrack** is a hybrid personal CO₂e (carbon dioxide equivalent) footprint estimator. It converts electricity bills and online shopping invoices into transparent, defensible estimates of your personal carbon footprint.

---

## 🎯 Research Question & Objective

> **Can a person's electricity bills and online purchase invoices be converted into a usable estimate of their personal carbon footprint?**

CarbonTrack addresses this by combining two rigorous calculation methodologies defined by the GHG Protocol:
1. **Activity-based estimation (High Data Quality)**: Used when physical quantity (kWh) is available from electricity bills.
2. **Spend-based estimation (Medium Data Quality)**: Used when only monetary purchase amount (₹) is available from shopping invoices.

---

## 🚀 Key Features

- **📄 Bill & Invoice Upload**: Direct text parsing (PDF) & Tesseract OCR (scanned images/JPG/PNG) for electricity bills and shopping invoices.
- **🛠️ Human Verification**: Mandatory verification step — user reviews and corrects OCR-extracted fields before calculation.
- **🏷️ Rule-based Categorization**: Automatic mapping of products and vendors to categories via keyword rules.
- **⚖️ Dual Methodology**: Activity-based calculation (kWh × factor) for electricity, spend-based (₹ × category factor) for purchases.
- **🔍 Calculation Transparency**: Every result shows its input, emission factor, formula, source, and version. "How was this calculated?" step-by-step breakdown per record.
- **📊 Dashboard**: Today's total, monthly total, and category breakdown.
- **🛡️ Versioned Emission Factors**: Every factor stored with value, unit, source, source_url, year, version, and boundary — never hard-coded.

---

## 🏗️ Project Architecture & Tech Stack

- **UI Framework**: Python + Streamlit
- **Database**: SQLite (`database/carbon.db`)
- **Data Engine**: Pandas & Plotly
- **PDF Extraction**: PyMuPDF (`fitz`)
- **OCR Engine**: Tesseract OCR & Pillow (`pytesseract`)
- **Testing**: Pytest

```
carbon-footprint-estimator/
├── app.py                     # Main Streamlit application entrypoint
├── requirements.txt           # Python dependencies
│
├── frontend/                  # Streamlit UI pages
│   ├── upload.py              # Bill/invoice upload + verification forms
│   └── dashboard.py           # Analytics dashboard + calculation explanations
│
├── backend/                   # Core processing logic
│   ├── calculator.py          # Activity & spend-based CO₂e calculation engine
│   ├── classifier.py          # Rule-based keyword → category mapper
│   ├── extractor.py           # PyMuPDF text & Tesseract OCR extraction
│   └── validators.py          # Input validation helpers
│
├── database/                  # SQLite database + schema
│   ├── carbon.db
│   └── db.py                  # SQLite interface & migrations
│
├── emission_factors/          # Reference emission factor data
│   ├── emission_factors.csv   # Cited factors with full metadata (15 fields)
│   └── category_rules.csv    # Keyword → category mapping rules
│
├── uploads/                   # User-uploaded bill/invoice files
│
├── sample_documents/          # Sample bills and invoices for testing
│
└── tests/                     # Unit & integration test suite
    ├── test_calculator.py
    └── test_pipeline.py
```

---

## 💻 Installation & Local Setup

### 1. Prerequisites
- Python 3.10+
- Tesseract OCR engine (required for scanned image OCR)

### 2. Setup Instructions

```bash
# Clone repository
git clone https://github.com/nikhilghotankar-8881/carbontrack.git
cd carbontrack

# Create & activate virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🧪 Running Tests

Run the full pytest suite:

```bash
pytest
```

---

## 📊 Citation & Emission Factor Methodology

Every emission factor used in CarbonTrack is stored with value, unit, method, country, region, source, source_url, year, version, boundary, and is_active flag:
- **Grid Electricity (India)**: Central Electricity Authority (CEA) CO₂ Baseline Database (0.7160 kg CO₂e / kWh).
- **Fuel & Activity Factors**: BEE / MoEFCC guidelines, UK DEFRA Conversion Factors & India MoPNG guidelines.
- **Transport Factors**: India GHG Program.
- **Spend-based EEIO Factors**: GHG Protocol EEIO Industry Average spend factors per category.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `PRD.md` | Product requirements — scope, objectives, acceptance criteria |
| `ARCHITECTURE.md` | System design — tech stack, folder structure, module responsibilities |
| `DESIGN.md` | Screen-by-screen UI/UX specification |
| `FLOW.md` | Pipeline diagrams — all data flows and processing steps |
| `PARAMETERS.md` | Data dictionary — every field, table, and schema definition |
| `PHASES.md` | Build roadmap — phase-by-phase development order |
| `ENHANCEMENTS.md` | Explicitly out-of-scope features and future ideas |

---

## 📜 License

MIT License. Developed for research and educational purposes.
