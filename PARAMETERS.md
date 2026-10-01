# Parameters — Data Dictionary

*Every field, table, and enum the app uses. This is the single source of truth for schemas — other docs reference it rather than repeating it.*

## 1. `emission_factors` Table

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer, PK | Auto-increment |
| `category` | text | e.g. "Electricity", "Fuel", "Clothing" |
| `activity_type` | text | e.g. "Grid Electricity", "Petrol", "Clothing Spend" |
| `unit` | text | Input unit, e.g. `kWh`, `litre`, `INR` |
| `factor_value` | float | The emission factor value itself |
| `factor_unit` | text | e.g. `kg CO₂e/kWh`, `kg CO₂e/INR` |
| `country` | text | e.g. "India" |
| `region` | text | e.g. "National", "Maharashtra" |
| `source` | text | e.g. "Central Electricity Authority" |
| `source_url` | text | URL to the source document |
| `year` | integer | Year the factor was published |
| `version` | text | e.g. "v22.0", "2023 Edition" |
| `boundary` | text | e.g. "Scope 2", "Cradle-to-gate" |
| `is_active` | boolean | Whether this factor is currently used (supports versioning) |

**Rule:** no factor is ever hard-coded in Python — every value the calculator uses comes from this table, and every row must have all fields filled in. Factor information is versioned rather than hard-coding one number into the application.

## 2. `documents` Table

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer, PK | Auto-increment |
| `user_id` | integer, FK | References `users.id` |
| `filename` | text | Original uploaded filename |
| `file_type` | text | `pdf`, `jpg`, `png` |
| `document_type` | text | `electricity_bill` or `shopping_invoice` |
| `upload_date` | datetime | When the document was uploaded |
| `raw_text` | text | Raw OCR/extracted text |
| `status` | text | `uploaded`, `extracted`, `verified`, `calculated` |

## 3. `extracted_items` Table

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer, PK | Auto-increment |
| `document_id` | integer, FK | References `documents.id` |
| `field_name` | text | e.g. "consumer_name", "units_consumed", "product_name" |
| `extracted_value` | text | Value as extracted by OCR |
| `verified_value` | text | Value after user verification/correction |
| `confidence` | float, nullable | OCR confidence score if available |

## 4. `calculations` Table

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer, PK | Auto-increment |
| `user_id` | integer, FK | References `users.id` |
| `document_id` | integer, FK | References `documents.id` |
| `date` | date | Transaction/bill date |
| `category` | text | Detected or assigned category |
| `activity_value` | float | The input quantity or amount used |
| `activity_unit` | text | e.g. `kWh`, `INR` |
| `factor_id` | integer, FK | References `emission_factors.id` |
| `factor_value` | float | The emission factor value at time of calculation |
| `method` | text | `activity-based` or `spend-based` |
| `source` | text | Factor source at time of calculation |
| `version` | text | Factor version at time of calculation |
| `result_co2e` | float | Calculated CO₂e in kg |

**Rule:** Every calculation retains the underlying activity data, factor, source, version, and method — never just the final carbon number. This enables the "How was this calculated?" feature and supports auditability.

## 5. `users` Table

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer, PK | Auto-increment |
| `name` | text | Default: "Local User" |
| `created_at` | datetime | Account creation timestamp |

Single local user for the prototype — no password, OTP, or session fields required.

## 6. Categories (initial set for MVP)

`Electricity`, `Fuel`, `Grocery`, `Clothing`, `Electronics`

Additional categories can be added later: `Transport`, `Household`, `Other`.

## 7. Electricity Bill Extracted Fields

`consumer_name`, `bill_date`, `units_consumed` (kWh), `bill_amount` (₹) — always shown to the user for verification before calculation (see `DESIGN.md`).

## 8. Shopping Invoice Extracted Fields

`product_name`, `quantity`, `amount` (₹), `date` — always shown to the user for verification before calculation (see `DESIGN.md`).

## 9. Category Rules — Keyword → Category Mapping

| Column | Notes |
|--------|-------|
| `keyword` | lowercase, normalized text fragment, e.g. `shirt`, `petrol`, `grocery` |
| `category` | one of the categories |

Example rows: `electricity→Electricity`, `petrol→Fuel`, `diesel→Fuel`, `rice→Food/Grocery`, `milk→Food/Grocery`, `shirt→Clothing`, `mobile→Electronics`. No match → falls back to `Other`.

## 10. Calculation Output Schema

The calculation engine returns this structure for every calculation:

```json
{
    "activity_value": 240,
    "activity_unit": "kWh",
    "factor_value": 0.716,
    "factor_unit": "kg CO₂e/kWh",
    "result_co2e": 171.84,
    "method": "activity-based",
    "source": "Central Electricity Authority",
    "version": "v22.0"
}
```

## 11. Calculation Formulas

```
Activity-based:  CO₂e = Activity Data × Emission Factor
Spend-based:     CO₂e = Purchase Amount × Category Spend Factor
```

## 12. File/Format Parameters

| Input | Accepted formats |
|-------|-----------------|
| Electricity bill upload | PDF, JPG, PNG |
| Shopping invoice upload | PDF, JPG, PNG |
| OCR engine | Tesseract OCR (locked choice — see `ENHANCEMENTS.md` for alternatives considered) |
| PDF text extraction | PyMuPDF |

## 13. Reference Emission Factor Sources (do not substitute invented numbers)

| Category | Preferred Source |
|----------|-----------------|
| Electricity (India) | Central Electricity Authority (CEA) — CO₂ Baseline Database |
| Fuel (India) | BEE / MoEFCC guidelines, UK DEFRA Conversion Factors |
| Transport (India) | India GHG Program |
| Spend-based categories | GHG Protocol spend-based method (economic value × EEIO factor) |
| Supplementary factors | UK Government's annual conversion-factor dataset, used only when no Indian factor exists |
