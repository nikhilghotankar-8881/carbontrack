# 🌱 CarbonTrack — Personal Carbon Footprint Estimator

**CarbonTrack** is a hybrid personal CO₂e (carbon dioxide equivalent) footprint estimator. It converts daily utility/fuel bills and online purchase records into a transparent, defensible estimate of your personal carbon footprint.

---

## 🎯 Research Question & Objective

> **Can a person's daily bills and online purchase records be converted into a usable estimate of their personal carbon footprint?**

CarbonTrack addresses this by combining two rigorous calculation methodologies defined by the GHG Protocol:
1. **Activity-based estimation (High Data Quality)**: Used when physical quantity (kWh, litres, kg, km) is available from bills or manual entries.
2. **Spend-based estimation (Medium Data Quality)**: Used when only monetary purchase amount (₹) is available from online purchase records.

---

## 🚀 Key Features

- **📄 Bill & Receipt Upload**: Direct text parsing (PDF) & Tesseract OCR (scanned images/JPG/PNG) for electricity, fuel, and grocery receipts.
- **🛠️ Verification Form**: Mandatory human-in-the-loop verification step before saving extracted fields.
- **🛒 Online Purchase CSV Import**: Bulk upload and auto-classify online purchase history (`date, vendor, product, amount`).
- **✍️ Manual Entry Form**: Flexible fallback for manual transaction inputs.
- **🏷️ Keyword Classifier**: Automatic mapping of products and vendors to 8 locked categories:
  `Electricity ⚡`, `Fuel ⛽`, `Transport 🚗`, `Food 🍎`, `Clothing 👕`, `Electronics 📱`, `Household 🏠`, `Other 📦`
- **📊 Interactive Dashboard**: KPI cards, category breakdown, daily trend line, monthly trend bar, and downloadable CSV report.
- **🌱 Rule-based Recommendation Engine**: Tailored, actionable carbon reduction tips matched to your highest-emitting category.
- **📜 Transaction History**: Full CRUD control to view, edit (with live recalculation), or delete past transactions.

---

## 🏗️ Project Architecture & Tech Stack

- **UI Framework**: Python + Streamlit (Multipage)
- **Database**: SQLite (`database/carbon.db`)
- **Data Engine**: Pandas & Plotly
- **PDF Extraction**: PyMuPDF (`fitz`)
- **OCR Engine**: Tesseract OCR & Pillow (`pytesseract`)
- **Testing**: Pytest

```
carbontrack/
├── app.py                     # Main Streamlit application entrypoint
├── requirements.txt           # Python dependencies
├── data/                      # Reference datasets
│   ├── emission_factors.csv   # Cited emission factors with source and year
│   └── category_rules.csv     # Keyword classification rules
├── database/                  # SQLite database location
│   └── carbon.db
├── modules/                   # Core system logic
│   ├── database.py            # SQLite database interface & migrations
│   ├── calculator.py          # Activity & spend-based CO₂e calculation engine
│   ├── classifier.py          # Keyword-based category classifier
│   ├── extractor.py           # PyMuPDF text & Tesseract OCR receipt parser
│   ├── recommendations.py     # Rule-based carbon reduction recommendations
│   ├── validators.py          # Input validation helpers
│   └── ui_components.py       # Reusable Streamlit UI components
├── pages/                     # Streamlit multipage views
│   ├── 1_Upload.py            # Bill upload & manual entry form
│   ├── 2_Purchases.py         # CSV import & preview table
│   ├── 3_Dashboard.py         # Analytics dashboard & insights
│   └── 4_History.py           # Transaction history CRUD
├── sample_data/               # Sample testing datasets
│   └── purchases.csv
└── tests/                     # Unit & integration test suite
    ├── test_calculator.py
    └── test_pipeline.py
```

---

## 💻 Installation & Local Setup

### 1. Prerequisites
- Python 3.10+
- Tesseract OCR engine (Optional for scanned image OCR)

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

Every emission factor used in CarbonTrack is stored with value, unit, method, region, source, and year:
- **Grid Electricity (India)**: Central Electricity Authority (CEA) CO₂ Baseline Database v22.0 (0.7160 kg CO₂e / kWh).
- **Fuel & Activity Factors**: UK DEFRA Conversion Factors & India MoPNG guidelines.
- **Spend-based EEIO Factors**: GHG Protocol EEIO Industry Average spend factors per category.

---

## 📜 License

MIT License. Developed for research and educational purposes.
