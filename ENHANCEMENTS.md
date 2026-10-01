# Enhancements — Explicitly Out of Scope for This Prototype

*This list exists so these ideas don't quietly creep back into the build. Nothing here should be started before the core pipeline in `PHASES.md` is finished and working.*

## 1. Excluded by Design (not "not yet" — genuinely not needed to prove the research idea)

| Excluded | Why |
|----------|-----|
| Manual entry form | MVP focuses on document upload → OCR → verification → calculation pipeline; manual entry adds a parallel input path without testing the core OCR+estimation pipeline |
| CSV bulk import of purchase history | MVP demonstrates per-invoice processing; bulk import is a convenience feature that doesn't test the core estimation logic |
| Direct Amazon/Flipkart account integration | Adds OAuth, API quota, and platform-approval overhead unrelated to the estimation research question |
| Bank/UPI/payment API integration | Financial-data access is a compliance burden the prototype doesn't need — spend data comes from invoices instead |
| ML-based product classification | Keyword rules are transparent, debuggable, and sufficient at this scale; an ML model adds training-data and evaluation overhead with no proportional benefit yet |
| AI/LLM-based recommendation engine | A rule-based lookup is fully sufficient and avoids unpredictable output; recommendations are not core to the estimation pipeline |
| Recommendation engine (any kind) | Not part of MVP scope — the prototype proves estimation, not behavioral nudging |
| Chatbot / conversational assistant | Not part of the estimation pipeline; would shift the demo's focus away from the calculation engine |
| Mobile app | Streamlit's browser UI is enough to demonstrate the prototype |
| Multi-user accounts, auth, OTP, social login | A single local user is enough to prove the calculation and dashboard logic |
| React + FastAPI + PostgreSQL rebuild | Adds a full second stack for no functional gain over Streamlit + SQLite at this scale |
| Cloud deployment | Not required to demonstrate the research contribution locally |
| All bill types (water, internet, etc.) | MVP proves the pipeline with electricity + shopping; adding more types is horizontal expansion, not validation |
| Every Indian product database | MVP uses a small verified dataset; expanding coverage comes after the pipeline works |
| Complete lifecycle carbon analysis | Beyond prototype scope — uses emission factors, not LCA methodology |
| Company carbon accounting | Prototype is personal footprint only |
| Complex prediction models | Not needed to demonstrate bill → CO₂e estimation |
| 20 different transport modes | Transport is not an MVP input type |
| Gamification, social sharing, carbon marketplace, blockchain ledger | None of these test whether bills/invoices can be turned into a usable footprint estimate |

## 2. Considered and Deliberately Not Locked In

| Idea | Status |
|------|--------|
| PaddleOCR instead of / alongside Tesseract | Considered during planning; Tesseract was locked in for simplicity. Worth revisiting only if OCR accuracy on real documents turns out to be a demo blocker |
| AI-based document classification | Considered; rule-based detection was locked in. For a mini-project demo, working rule-based mapping is better than adding AI that doesn't improve reliability |

## 3. Realistic Post-Prototype Ideas (only after Phase 12 is done and demoed)

- Manual entry form as a fallback input method
- CSV bulk import for online purchase history
- Wider emission-factor coverage (more regions, more activity types) — still sourced, never invented
- A smarter, still-transparent classifier (e.g. fuzzy matching) before ever reaching for ML
- Rule-based recommendation engine (highest category → matching suggestion)
- Transaction history page with edit/delete capabilities
- Exporting the data-quality methodology as a short public write-up
- Multi-user support, only if the project moves beyond a single-person demo

## 4. One-Line Test Before Adding Anything from This File

> Does this help answer "can electricity bills + shopping invoices become a usable personal CO₂e estimate," or does it just make the project bigger?

If the honest answer is the second one, it stays in this file.
