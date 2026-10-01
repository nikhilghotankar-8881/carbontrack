# Design

*Screen-by-screen UI/UX spec. For the underlying data, see `PARAMETERS.md`; for the logic behind each screen, see `FLOW.md`.*

## 1. Navigation

Two primary actions + dashboard — no nested menus, no login screen:

```
[Upload Bill]  |  [Upload Shopping Invoice]  |  Dashboard
```

## 2. Visual Identity

- Green / environmental palette (e.g. deep green + off-white + a warning amber reserved for spend-based quality badges)
- Clean, minimal layout — no decorative illustrations, no gamification badges, no social feed
- Every numeric result is shown with its unit (`kg CO₂e`) and never as a bare number

## 3. Home Screen (Phase 1)

```
┌─────────────────────────────────────────────────────────┐
│               🌱 Carbon Footprint Estimator             │
│                                                         │
│    Transform your bills and purchase invoices into       │
│    transparent CO₂e estimates.                          │
│                                                         │
│    ┌──────────────────┐  ┌──────────────────────────┐   │
│    │  📄 Upload Bill  │  │  🛒 Upload Shopping       │   │
│    │                  │  │     Invoice               │   │
│    └──────────────────┘  └──────────────────────────┘   │
│                                                         │
│                    📊 Dashboard                          │
└─────────────────────────────────────────────────────────┘
```

## 4. Upload Bill Page

1. File uploader — accepts PDF, JPG, PNG
2. On upload: show a spinner ("Reading your bill…"), then the **Verification Form** (see §6)

## 5. Upload Shopping Invoice Page

1. File uploader — accepts PDF, JPG, PNG
2. On upload: show a spinner ("Reading your invoice…"), then the **Verification Form** (see §6)

## 6. Human Verification Screen (Phase 5) — reused for both document types

### For Electricity Bill:

```
┌──────────────────────────────────────────────────────┐
│              🛠️ Verify Extracted Bill Data            │
│                                                      │
│  Consumer Name                                       │
│  [Nikhil                                          ]  │
│                                                      │
│  Units Consumed                                      │
│  [240 kWh                                         ]  │
│                                                      │
│  Bill Amount                                         │
│  [₹1850                                          ]  │
│                                                      │
│  Date                                                │
│  [28/09/2026                                      ]  │
│                                                      │
│              [ ✅ Confirm & Calculate ]               │
└──────────────────────────────────────────────────────┘
```

### For Shopping Invoice:

```
┌──────────────────────────────────────────────────────┐
│           🛠️ Verify Extracted Invoice Data           │
│                                                      │
│  Product                                             │
│  [Cotton T-Shirt                                  ]  │
│                                                      │
│  Quantity                                            │
│  [1                                               ]  │
│                                                      │
│  Amount                                              │
│  [₹799                                           ]  │
│                                                      │
│  Date                                                │
│  [30/09/2026                                      ]  │
│                                                      │
│              [ ✅ Confirm & Calculate ]               │
└──────────────────────────────────────────────────────┘
```

Every field is editable — the user never has to trust OCR blindly. If a field couldn't be extracted, the input is left blank and highlighted, not silently zero.

## 7. Result Display (Phase 7 / Phase 8)

### Electricity Bill Result:

```
┌──────────────────────────────────────────────────────┐
│              Estimated Carbon Footprint               │
│                                                      │
│              XXX kg CO₂e                             │
│                                                      │
│  Activity:        240 kWh                            │
│  Method:          Activity-based                     │
│  Emission Factor: XXX kg CO₂e/kWh                   │
│  Source:          Central Electricity Authority       │
│  Version:         XXX                                │
│                                                      │
│              [🔍 How was this calculated?]            │
└──────────────────────────────────────────────────────┘
```

### Shopping Invoice Result:

```
┌──────────────────────────────────────────────────────┐
│              Estimated Carbon Footprint               │
│                                                      │
│  Product:         Cotton T-Shirt                     │
│  Category:        Clothing                           │
│  Quantity:        1                                   │
│  Purchase Value:  ₹799                               │
│  Method:          Category/Spend-based               │
│  Estimated Carbon: XX kg CO₂e                       │
│  Source:          XXXXXXXX                            │
│                                                      │
│              [🔍 How was this calculated?]            │
└──────────────────────────────────────────────────────┘
```

## 8. "How Was This Calculated?" Explanation (Phase 11)

### For Electricity:

```
┌──────────────────────────────────────────────────────┐
│           How was this calculated?                    │
│                                                      │
│  INPUT                                               │
│  240 kWh                                             │
│           ↓                                          │
│  EMISSION FACTOR                                     │
│  XXX kg CO₂e/kWh                                    │
│           ↓                                          │
│  FORMULA                                             │
│  240 × XXX                                           │
│           ↓                                          │
│  RESULT                                              │
│  XXX kg CO₂e                                        │
│           ↓                                          │
│  SOURCE                                              │
│  Central Electricity Authority                       │
└──────────────────────────────────────────────────────┘
```

### For Shopping:

```
┌──────────────────────────────────────────────────────┐
│           How was this calculated?                    │
│                                                      │
│  INPUT                                               │
│  ₹799                                                │
│           ↓                                          │
│  CATEGORY                                            │
│  Clothing                                            │
│           ↓                                          │
│  CATEGORY FACTOR                                     │
│  XXX kg CO₂e/INR                                    │
│           ↓                                          │
│  FORMULA                                             │
│  Spend-based calculation                             │
│           ↓                                          │
│  RESULT                                              │
│  XX kg CO₂e                                         │
└──────────────────────────────────────────────────────┘
```

## 9. Dashboard (Phase 10)

```
┌──────────────────────────────────────────────────────┐
│                 CARBON FOOTPRINT                      │
│                                                      │
│  ┌────────────────────┐  ┌────────────────────┐      │
│  │ Today              │  │ This Month          │      │
│  │ XXX kg CO₂e        │  │ XXX kg CO₂e         │      │
│  └────────────────────┘  └────────────────────┘      │
│                                                      │
│  Category Breakdown                                  │
│  Electricity    XX kg                                │
│  Shopping       XX kg                                │
│  Food           XX kg                                │
│  Fuel           XX kg                                │
│                                                      │
│  Recent Calculations                                 │
│  Electricity Bill       XX kg                        │
│  Online Purchase        XX kg                        │
│  Grocery Receipt        XX kg                        │
└──────────────────────────────────────────────────────┘
```

## 10. Error / Empty States

| Situation | What's shown |
|-----------|-------------|
| No calculations yet | Dashboard shows "No data yet — upload a bill or shopping invoice to see your footprint" |
| Unreadable/empty upload | "Couldn't read this file — please try a clearer image" |
| OCR couldn't extract a field | Field left blank and highlighted in the verification form, user fills manually |
| Category not recognized | Falls back to "Other" and is visibly flagged as auto-assigned, inviting a manual fix |
| Unknown product | "Unable to identify this product. Please verify or select a category manually." |
| Missing quantity | "Unable to identify quantity. Please verify or enter the value manually." |
| Unsupported document | "This document type is not supported. Please upload an electricity bill or shopping invoice." |
| Duplicate invoice | Warning shown, user can choose to proceed or skip |
