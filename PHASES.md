# Phases

*The build order. Two views of the same roadmap: a fast MVP track, and the fuller phase breakdown once the MVP works. Build top to bottom — don't skip ahead to later phases before the ones above them are solid.*

## Fast MVP track (build this first, in this order)

| Phase | Add | Proves |
|---|---|---|
| 1 | Manual entry → category → emission factor → CO₂e → dashboard | The calculation engine actually works |
| 2 | Bill/receipt upload → text/OCR extraction → verification → calculation | Real bills can enter the pipeline |
| 3 | CSV upload → classification → spend-based calculation | Online purchases can enter the pipeline |
| 4 | Daily + monthly + category-wise dashboard | The user can see their own footprint |
| 5 | Highest-category → recommendation | The output is actionable, not just a number |

Stop here for a demoable prototype. Everything below is what makes the demo *stronger*, not what makes it *work*.

## Full phase roadmap

| Phase | Deliverable |
|---|---|
| 0 | Frozen scope + one-page architecture/requirements doc |
| 1 | Empty Streamlit app runs (`streamlit run app.py`) |
| 2 | Emission-factor database — every factor has value, unit, method, source, year |
| 3 | Calculation engine (`calculate_activity_emission`, `calculate_spend_emission`, `calculate_total_emission`) with ≥10 independent test cases, tested before any UI exists |
| 4 | Manual-entry form wired end-to-end to the calculation engine |
| 5 | SQLite `transactions` table + History page (view/edit/delete, no auth) |
| 6 | CSV import: preview → confirm → save multiple purchases at once |
| 7 | Keyword-based category classifier + manual correction + "Other" fallback |
| 8 | Text-based PDF extraction (PyMuPDF) + verification form |
| 9 | OCR (Tesseract) for scanned/image bills — at least 3 realistic bill formats working |
| 10 | Unified pipeline: manual, CSV, and bill inputs all produce the same standardized transaction record |
| 11 | Dashboard: KPI cards, category chart, daily trend, monthly trend, transaction table |
| 12 | Rule-based recommendation engine (no AI) |
| 13 | Data-quality/transparency labels on every result (method, source, High/Medium quality) |
| 14 | Test suite: calculation, input validation, OCR quality, dashboard edge cases; manual-vs-system calculation cross-check |
| 15 | Controlled one-month demo dataset (3 bill types + 3 online purchases) |
| 16 | Final polish: navigation, green visual identity, input validation, error states, loading indicators, downloadable CSV report, README, screenshots |

## Critical path

```
Calculation Engine -> Manual Entry -> SQLite History -> CSV Purchases
   -> Bill Extraction -> OCR -> Unified Pipeline -> Dashboard -> Recommendations
```

- **End of Phase 4:** a functioning manual carbon estimator already exists
- **End of Phase 6:** the core online-purchase solution works
- **End of Phase 10:** the full research prototype is functional — everything after this strengthens the demo without changing the core system

## What NOT to do mid-roadmap

Don't start Phase 8–9 (bill OCR) before Phase 3's calculation engine has passed its own test cases — a broken calculator makes every later phase impossible to trust. Don't polish the dashboard (Phase 11+) before Phase 10's unified pipeline is in place, or you'll be redoing chart logic twice.
