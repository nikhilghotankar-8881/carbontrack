# Parameters — Data Dictionary

*Every field, table, and enum the app uses. This is the single source of truth for schemas — other docs reference it rather than repeating it.*

## 1. `emission_factors` table

| Field | Type | Notes |
|---|---|---|
| `id` | integer, PK | |
| `category` | text | One of the 8 categories (§4) |
| `activity` | text | e.g. "Electricity", "Petrol", "Clothing spending" |
| `unit` | text | e.g. `kWh`, `litre`, `INR` |
| `factor` | float | The emission factor value itself |
| `method` | text | `activity` or `spend` |
| `source` | text | e.g. "CEA CO2 Baseline Database v22.0", "GHG Protocol EEIO" |
| `source_year` | integer | Year the factor was published |
| `region` | text | e.g. "India" |

**Rule:** no factor is ever hard-coded in Python — every value the calculator uses comes from this table, and every row must have all 9 fields filled in.

## 2. `transactions` table

| Field | Type | Notes |
|---|---|---|
| `id` | integer, PK | |
| `date` | date | |
| `vendor` | text | |
| `item` | text | |
| `category` | text | One of the 8 categories |
| `amount` | float | Currency amount (₹) |
| `quantity` | float, nullable | Physical quantity, if known |
| `unit` | text, nullable | e.g. `kWh`, `litre` |
| `co2e` | float | Calculated result, in kg |
| `calculation_method` | text | `activity-based` or `spend-based` |
| `source_type` | text | `manual`, `bill`, or `csv` |

## 3. `users` table

Single local user for the prototype — no password, OTP, or session fields required.

## 4. Categories (locked list)

`Electricity`, `Fuel`, `Transport`, `Food`, `Clothing`, `Electronics`, `Household`, `Other`

## 5. Online purchase CSV — required columns

```
date,vendor,product,amount
2026-09-20,Amazon,Cotton T-Shirt,799
2026-09-21,Flipkart,Earbuds,1499
2026-09-22,BigBasket,Grocery,650
```

Optional extra columns accepted if present: `category` (skips auto-classification for that row), `quantity`, `unit`.

## 6. Bill/receipt extracted fields

`date`, `vendor`, `item`, `quantity`, `unit`, `amount` — always shown to the user for verification before saving (see `DESIGN.md` §4).

## 7. `category_rules.csv` — keyword → category mapping

| Column | Notes |
|---|---|
| `keyword` | lowercase, normalized text fragment, e.g. `shirt`, `petrol`, `grocery` |
| `category` | one of the locked categories (§4) |

Example rows: `shirt→Clothing`, `jeans→Clothing`, `petrol→Fuel`, `diesel→Fuel`, `grocery→Food`, `milk→Food`, `phone→Electronics`, `laptop→Electronics`. No match → falls back to `Other`.

## 8. Calculation parameters

| Enum field | Values |
|---|---|
| `calculation_method` | `activity-based`, `spend-based` |
| `data_quality` | `High` (activity-based), `Medium` (spend-based) |
| `source_type` | `manual`, `bill`, `csv` |

Formulas:
```
Activity-based:  CO2e = quantity × emission_factor
Spend-based:     CO2e = amount × spend_emission_factor
Total footprint: sum(co2e) across all saved transactions
```

## 9. File/format parameters

| Input | Accepted formats |
|---|---|
| Bill/receipt upload | PDF, JPG, PNG |
| Online purchase upload | CSV |
| OCR engine | Tesseract OCR (locked choice — see `ENHANCEMENTS.md` for alternatives considered) |
| PDF text extraction | PyMuPDF |

## 10. Reference emission-factor sources (do not substitute invented numbers)

| Category | Preferred source |
|---|---|
| Electricity (India) | Central Electricity Authority — CO₂ Baseline Database, currently v22.0 |
| Spend-based categories | GHG Protocol spend-based method (economic value × EEIO factor) |
| Supplementary activity factors | UK Government's annual conversion-factor dataset, used only when no Indian factor exists |
