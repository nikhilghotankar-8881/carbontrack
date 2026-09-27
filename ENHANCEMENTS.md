# Enhancements — Explicitly Out of Scope for This Prototype

*This list exists so these ideas don't quietly creep back into the build. Nothing here should be started before the core pipeline in `PHASES.md` is finished and working.*

## 1. Excluded by design (not "not yet" — genuinely not needed to prove the research idea)

| Excluded | Why |
|---|---|
| Direct Amazon/Flipkart account integration | Adds OAuth, API quota, and platform-approval overhead unrelated to the estimation research question; CSV upload proves the same pipeline |
| Bank/UPI/payment API integration | Financial-data access is a compliance burden the prototype doesn't need — spend data comes from receipts/CSV instead |
| ML-based product classification | Keyword rules are transparent, debuggable, and sufficient at this scale; an ML model adds training-data and evaluation overhead with no proportional benefit yet |
| AI/LLM-based recommendation engine | A rule-based lookup (highest category → matching tip) is fully sufficient and avoids unpredictable output |
| Chatbot / conversational assistant | Not part of the estimation pipeline; would shift the demo's focus away from the calculation engine |
| Mobile app | Streamlit's browser UI is enough to demonstrate the prototype |
| Multi-user accounts, auth, OTP, social login | A single local user is enough to prove the calculation and dashboard logic |
| React + FastAPI + PostgreSQL rebuild | Adds a full second stack for no functional gain over Streamlit + SQLite at this scale |
| Cloud deployment | Not required to demonstrate the research contribution locally |
| Gamification, social sharing, carbon marketplace, blockchain ledger | None of these test whether bills/purchases can be turned into a usable footprint estimate — the one thing this prototype exists to prove |

## 2. Considered and deliberately not locked in

| Idea | Status |
|---|---|
| PaddleOCR instead of / alongside Tesseract | Considered during planning; Tesseract was locked in for simplicity. Worth revisiting only if OCR accuracy on real receipts turns out to be a demo blocker |
| Excel (`.xlsx`) upload in addition to CSV | Mentioned as an option early on; CSV was locked as the single supported format to keep the import validator simple |

## 3. Realistic post-prototype ideas (only after Phase 16 is done and demoed)

- Wider emission-factor coverage (more regions, more activity types) — still sourced, never invented
- A smarter, still-transparent classifier (e.g. fuzzy matching) before ever reaching for ML
- Exporting the data-quality methodology as a short public write-up, since the activity-vs-spend distinction is the prototype's actual research contribution
- Multi-user support, only if the project moves beyond a single-person demo

## 4. One-line test before adding anything from this file

> Does this help answer "can bills + purchase records become a usable personal CO₂e estimate," or does it just make the project bigger?

If the honest answer is the second one, it stays in this file.
