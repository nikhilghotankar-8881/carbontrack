# PRD — Personal Carbon Footprint Estimator

## 1. Research question

Can a person's daily bills and online purchase records be converted into a usable estimate of their personal carbon footprint?

The prototype exists to answer this — nothing else. It is a **Bill + Purchase → CO₂e Estimator**, not a banking app, an e-commerce app, or a generic AI assistant.

## 2. Target user

An individual (e.g. a household member, a student for a college project demo) who wants a rough, defensible estimate of their monthly carbon footprint from bills they already have and purchases they already made — with no manual carbon-accounting expertise required.

## 3. Objectives

- Turn everyday inputs (electricity/fuel/grocery bills, online purchase history, manual entries) into a standardized CO₂e estimate
- Clearly separate **activity-based** (precise) estimates from **spend-based** (approximate) estimates — never blur the two
- Show the user where their footprint comes from and one actionable way to reduce it
- Keep every number traceable to a documented emission factor — never invented

## 4. Scope

### In scope — 3 input methods only
1. Bill/receipt upload — electricity, LPG/fuel, grocery/food, shopping receipt (PDF/JPG/PNG)
2. Online purchase CSV upload (`date, vendor, product, amount`)
3. Manual entry — fallback when a bill can't be read

### Out of scope (see `ENHANCEMENTS.md` for the full deferred list)
No direct Amazon/Flipkart/bank/UPI integration, no ML classifier, no AI recommendation engine, no chatbot, no mobile app, no multi-user auth, no cloud deployment requirement, no blockchain.

## 5. Functional requirements

| ID | Requirement |
|---|---|
| FR1 | User can upload a bill/receipt (PDF/JPG/PNG) |
| FR2 | System extracts date, vendor, item, quantity, unit, amount from the bill (direct text for text-PDFs, OCR for scans/images) |
| FR3 | User can review and edit every extracted field before it's saved |
| FR4 | User can upload a CSV of online purchases and preview parsed rows before import |
| FR5 | User can manually enter a transaction (date, category, item, amount, quantity, unit) |
| FR6 | System classifies each item into one of 8 categories via keyword rules, with manual override |
| FR7 | System calculates CO₂e using activity-based method when a physical quantity is known |
| FR8 | System calculates CO₂e using spend-based method when only a purchase amount is known |
| FR9 | Every transaction is saved with its category, amount, CO₂e, method, and source type (manual/bill/csv) |
| FR10 | Dashboard shows total, daily, and monthly CO₂e, plus category breakdown and the highest-emitting category |
| FR11 | System shows one rule-based reduction recommendation matched to the highest-emitting category |
| FR12 | Every CO₂e result displays its method and a data-quality label (High for activity-based, Medium for spend-based) |
| FR13 | User can view, edit, and delete past transactions in a history page |

## 6. Non-functional requirements

- Every emission factor stored must carry value, unit, method, source, and year — no hard-coded numbers in application code
- Single local user is sufficient — no authentication, OTP, or social login
- Runs locally via Streamlit; no cloud dependency required for the first prototype
- Extraction never auto-saves without user verification, since receipt layouts vary too much to trust blindly

## 7. Acceptance criteria (what a judge/reviewer should be able to do)

1. Upload an electricity bill showing 185 kWh → system reads it and returns an activity-based CO₂e estimate
2. Upload a purchase CSV containing an Amazon T-shirt (₹799) → system classifies it as Clothing and returns a spend-based CO₂e estimate
3. Combine several transactions across categories → dashboard shows a correct category-wise and total breakdown
4. Dashboard correctly names the highest-emitting category and shows one matching recommendation

## 8. What this product deliberately does not claim

> We estimate personal CO₂e using activity-based factors where physical consumption is available, and spend-based/category-level factors where only purchase value is available.

It never claims to calculate the exact carbon footprint of a specific product — the GHG Protocol itself recognizes multiple valid calculation approaches (supplier-specific, hybrid, average-data, spend-based) depending on what data exists.

## 9. Research contribution

A practical hybrid estimator that reduces manual data entry while honestly distinguishing precise activity-based calculations from approximate spend-based estimates.
