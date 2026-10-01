# PRD — Personal Carbon Footprint Estimator

## 1. Research Question

Can a person's daily electricity bills and online purchase invoices be converted into a usable, transparent estimate of their personal carbon footprint?

The prototype exists to answer this — nothing else. It is a **Bill + Invoice → CO₂e Estimator**, not a banking app, an e-commerce app, or a generic AI assistant.

## 2. Target User

An individual (e.g. a household member, a student for a college project demo) who wants a rough, defensible estimate of their monthly carbon footprint from bills and purchase invoices they already have — with no manual carbon-accounting expertise required.

## 3. Objectives

- Turn two everyday document types (electricity bill, online shopping invoice) into a standardized CO₂e estimate
- Clearly separate **activity-based** (precise) estimates from **spend-based** (approximate) estimates — never blur the two
- Show the user exactly how each estimate was calculated (input → factor → formula → result → source)
- Keep every number traceable to a documented emission factor — never invented
- Let the user verify and correct OCR-extracted data before calculation

## 4. Scope

### In scope — 2 input types only
1. **Electricity bill upload** — PDF/JPG/PNG (OCR extraction → verification → activity-based calculation)
2. **Online shopping invoice upload** — Amazon/Flipkart-style invoice (OCR extraction → verification → category/spend-based calculation)

### Out of scope (see `ENHANCEMENTS.md` for the full deferred list)
No manual entry form, no CSV bulk import, no direct Amazon/Flipkart API integration, no bank/UPI integration, no ML classifier, no AI recommendation engine, no chatbot, no mobile app, no multi-user auth, no cloud deployment, no blockchain, no gamification.

## 5. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | User can upload an electricity bill (PDF/JPG/PNG) |
| FR2 | User can upload an online shopping invoice (PDF/JPG/PNG) |
| FR3 | System extracts structured fields from uploaded documents via OCR (consumer name, bill date, units consumed, amount for electricity; product, quantity, amount, date for shopping) |
| FR4 | User can review and edit every extracted field before calculation proceeds (mandatory verification step) |
| FR5 | System detects document category and maps to the correct emission factor |
| FR6 | System calculates CO₂e using activity-based method when physical quantity is known (e.g. kWh) |
| FR7 | System calculates CO₂e using spend-based method when only purchase amount is known |
| FR8 | Every calculation result displays: estimated CO₂e, calculation method, emission factor used, source, and version |
| FR9 | Every calculation is saved with full metadata: activity data, factor, source, version, method, result |
| FR10 | Dashboard shows today's total, this month's total, and category breakdown |
| FR11 | User can click "How was this calculated?" on any record to see the full step-by-step breakdown (input → factor → formula → result → source) |
| FR12 | System handles edge cases gracefully: poor-quality images, OCR errors, unknown products, missing quantities, unsupported documents |

## 6. Non-Functional Requirements

- Every emission factor stored must carry: value, unit, country, region, source, source_url, year, version, boundary, and is_active flag — no hard-coded numbers in application code
- Emission factors are versioned, not hard-coded into a single number
- Single local user is sufficient — no authentication, OTP, or social login
- Runs locally; no cloud dependency required for the prototype
- OCR never auto-calculates — extraction and calculation are separate steps
- Extraction never auto-saves without user verification

## 7. Acceptance Criteria (what a judge/reviewer should be able to do)

1. Upload an electricity bill showing 240 kWh → system reads it, user confirms extracted data, system returns an activity-based CO₂e estimate with CEA factor and source
2. Upload a shopping invoice showing a Cotton T-Shirt (₹799) → system classifies as Clothing, returns spend-based CO₂e estimate with source
3. Click "How was this calculated?" → see the full breakdown: input value, emission factor, formula, result, source
4. Dashboard shows correct today/monthly totals and category breakdown
5. Upload a poor-quality image → system shows graceful message instead of crashing

## 8. What This Product Deliberately Does NOT Claim

> We estimate personal CO₂e using activity-based factors where physical consumption is available, and spend-based/category-level factors where only purchase value is available.

It never claims to calculate the exact carbon footprint of a specific product. The GHG Protocol itself recognizes multiple valid calculation approaches depending on what data exists. Shopping estimates are presented as **estimated values** based on the chosen factor/method.

## 9. Research Contribution

A practical hybrid estimator that converts everyday bills and purchase invoices into transparent, traceable carbon footprint estimates — with every calculation backed by its activity data, emission factor, source, and method.
