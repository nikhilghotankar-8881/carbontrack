# Phases — Build Roadmap

*The build order for the working demo. Build top to bottom — don't skip ahead to later phases before the ones above them are solid.*

## MVP Scope Lock (Phase 0)

Two document types only:
1. Electricity bill
2. Online shopping invoice

Core output per calculation: Estimated CO₂e + Calculation method + Emission factor + Source + Daily total + Monthly total.

**Do NOT build:** all bill types, every Indian product, advanced AI, complete lifecycle carbon analysis, company carbon accounting, complex prediction, 20 transport modes.

---

## Phase Roadmap

| Phase | Deliverable | Done When |
|-------|-------------|-----------|
| **0 — Freeze MVP Scope** | Decide exactly what the prototype will demonstrate. Two document types → one reliable calculation pipeline. | Scope is documented and frozen |
| **1 — Project Foundation** | Complete application skeleton running. Backend stubs for `/upload`, `/extract`, `/verify`, `/factors`, `/calculate`, `/records`, `/dashboard`. Database with `users`, `documents`, `extracted_items`, `emission_factors`, `calculations` tables. | App opens and shows: "Carbon Footprint Estimator", [Upload Bill], [Upload Shopping Invoice], Dashboard |
| **2 — Emission Factor Database** | Emission factors table with 15 fields (id, category, activity_type, unit, factor_value, factor_unit, country, region, source, source_url, year, version, boundary, is_active). Initial verified data for Electricity, Fuel, Grocery, Clothing, Electronics. | Can query: Category=Electricity, Unit=kWh, Factor=[verified value], Source=CEA, Version=[version] and get the correct factor |
| **3 — Calculation Engine** | Activity-based: `CO₂e = Activity Data × Emission Factor`. Spend-based fallback for shopping. Engine returns: `activity_value`, `activity_unit`, `factor_value`, `factor_unit`, `result_co2e`, `method`, `source`, `version`. | Enter 240 kWh → backend returns calculated CO₂e with factor and source |
| **4 — Bill Upload + OCR** | Upload Image/PDF → OCR → Extracted text → Structured data. Electricity bill extracts: consumer name, bill date, units consumed, amount. OCR only reads the document — calculation engine is separate. | Upload a bill image → get structured extracted fields |
| **5 — Human Verification Screen** | After OCR, show editable form: Consumer Name, Units Consumed, Bill Amount, Date + [Confirm] button. User can verify or correct extracted values before calculation. | Upload → OCR → editable extracted fields → Confirm |
| **6 — Categorization + Factor Mapping** | Category detection → Emission factor selection. Rule-based mapping: electricity→Electricity, petrol→Fuel, rice→Food, shirt→Clothing, mobile→Electronics. | App displays: Category=Electricity, Unit=kWh, Factor=XXX, Source=CEA, Version=XXX |
| **7 — Complete Electricity Bill Demo** | Full end-to-end: Upload → OCR → Extract → User Confirms → Category=Energy → Activity=240 kWh → Find CEA Factor → Calculate CO₂e → Save → Show Result with method, factor, source. | Upload electricity bill → see result with full transparency |
| **8 — Online Shopping Invoice** | Upload Amazon/Flipkart-style invoice → OCR extracts product, quantity, amount, date → Category mapping → Spend-based calculation → Estimated CO₂e with source and method. | Upload shopping invoice → see estimated CO₂e per product |
| **9 — Save Every Calculation** | Every calculation saves: user_id, document_id, date, category, activity_value, activity_unit, factor_id, factor_value, method, source, version, result_co2e. | All calculations are persisted with full metadata |
| **10 — Dashboard** | Today total, This Month total, Category breakdown (Electricity/Shopping/Food/Fuel), Recent calculations list. | Dashboard shows aggregated daily/monthly/category data |
| **11 — "How Was This Calculated?"** | Per-record explanation: Input → Emission Factor → Formula → Result → Source. For electricity: `240 × factor = XXX kg CO₂e, Source: CEA`. For shopping: `₹799 → Clothing → category factor → spend-based → XX kg CO₂e`. | Click "How was this calculated?" on any record → see full step-by-step breakdown |
| **12 — Demo Safety Checks** | Test: normal bill, poor-quality image, OCR wrong value (user edits), unknown product, duplicate invoice, missing quantity, unsupported document. App never crashes — shows graceful messages like "Unable to identify quantity. Please verify or enter the value manually." | All 7 test scenarios handled without crashes |

---

## Critical Path

```
Emission Factor DB → Calculation Engine → OCR → Verification UI → Factor Mapping
    → Electricity Bill End-to-End → Shopping Invoice End-to-End
    → Save Calculations → Dashboard → Calculation Explanation → Safety Checks
    → JUDGE DEMO
```

## Milestones

- **End of Phase 7:** First major milestone — a legitimate working prototype for electricity bills
- **End of Phase 8:** Both document types working — the full MVP scope is functional
- **End of Phase 11:** Complete transparency feature — the strongest demo point
- **Phase 12 complete:** Demo-ready with safety checks

## What NOT to do mid-roadmap

Don't start Phase 4 (OCR) before Phase 3's calculation engine works — a broken calculator makes every later phase impossible to trust. Don't polish the dashboard (Phase 10) before Phase 9's save-every-calculation is in place, or you'll be redoing aggregation logic twice. Don't add AI classification — for a mini-project demo, working rule-based mapping is better than AI that doesn't improve reliability.

## Phase 13 — Final Judge Demo (5–7 minutes)

| Demo Part | Content |
|-----------|---------|
| Part 1 | Explain problem: "People have bills and purchase records, but those records show financial expenditure rather than environmental impact." |
| Part 2 | Upload electricity bill → OCR → 240 kWh → Confirm |
| Part 3 | Show factor: Electricity → CEA → factor |
| Part 4 | Calculate: 240 × factor → XXX kg CO₂e |
| Part 5 | Show transparency: Source, Method, Factor, Formula, Result |
| Part 6 | Upload online invoice → Product → Category → Factor → Estimated CO₂e |
| Part 7 | Dashboard: Today XXX kg, This Month XXX kg |

**Closing statement:** "Every calculation is stored with its activity data, emission factor, source and method, so the user can understand how the estimate was generated."
