# Design

*Screen-by-screen UI/UX spec. For the underlying data, see `PARAMETERS.md`; for the logic behind each screen, see `FLOW.md`.*

## 1. Navigation

Four pages, flat navigation (Streamlit sidebar or top nav) — no nested menus, no login screen:

```
Upload  |  Purchases  |  Dashboard  |  History
```

## 2. Visual identity

- Green / environmental palette (e.g. deep green + off-white + a warning amber reserved for "Medium" data-quality badges)
- Clean, minimal layout — no decorative illustrations, no gamification badges, no social feed
- Every numeric result is shown with its unit (`kg CO₂e`) and never as a bare number

## 3. Category icons (for chips, dropdowns, chart legends)

| Category | Icon |
|---|---|
| Electricity | ⚡ |
| Fuel | ⛽ |
| Transport | 🚗 |
| Food | 🍎 |
| Clothing | 👕 |
| Electronics | 📱 |
| Household | 🏠 |
| Other | 📦 |

## 4. Upload page (bills/receipts)

1. File uploader — accepts PDF, JPG, PNG
2. On upload: show a spinner ("Reading your bill…"), then a **"Verify extracted information"** form:

```
Vendor       [XYZ Electricity      ]
Date         [25/09/2026           ]
Quantity     [185                  ]
Unit         [kWh                  ]
Amount       [1640                 ]

           [ Confirm ]
```

Every field is editable — the user never has to trust OCR blindly. If a field couldn't be extracted, the input is left blank and highlighted, not silently zero.

3. On confirm: show the calculated result card (see §6) and a "Saved to history" toast.

## 5. Purchases page (CSV import)

1. File uploader for the purchase CSV, with a link to a sample-format download
2. Preview table before anything is saved:

```
3 records found

Date       Product        Category      Amount
20 Sep     T-Shirt        Clothing      ₹799
21 Sep     Earbuds        Electronics   ₹1,499
22 Sep     Grocery        Food          ₹650

        [ Confirm Import ]
```

3. Category column is editable inline — if the classifier got something wrong, the user fixes it here before import, not after.

## 6. Result display component (reused on Upload, Purchases, Manual Entry)

```
Estimated CO2e
4.82 kg

Method:            Activity-based
Data used:         185 kWh
Emission factor:   India / Electricity (CEA v22.0)
Data quality:      ● High
```

For a spend-based result, the same layout with `Data quality: ● Medium` and the underlying amount instead of a physical quantity. The quality dot is a simple color chip (green = High, amber = Medium) — never hidden, never optional.

## 7. Manual entry form

```
Date        [ 27-09-2026 ▾ ]
Category    [ Transport   ▾ ]
Item        [ Petrol         ]
Quantity    [ 5              ]
Unit        [ litres      ▾ ]
Amount      [ ₹ 500          ]

           [ Calculate & Save ]
```

## 8. Dashboard

```
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────────┐
│ Total CO2e    │ │ This Month    │ │ Transactions  │ │ Highest Category  │
│ 86.4 kg       │ │ +12%          │ │ 24            │ │ Transportation     │
└───────────────┘ └───────────────┘ └───────────────┘ └───────────────────┘

Category Breakdown                     Daily Trend
Transportation  ████████████ 40%       kg CO2e
Electricity     █████████    27%       ▂▃▂▄▆▃▂▅▇▄▃▂
Food            ██████       18%
Shopping        ███           9%       Monthly Trend
Other           ██            6%       ▂▃▅▆▇

Transaction Table
Date | Item | Category | Amount | CO2e | Method

┌─────────────────────────────────────────────┐
│ Transportation is your largest source        │
│ this month. Consider public transport,       │
│ walking or carpooling where practical.        │
└─────────────────────────────────────────────┘
```

Charts are Plotly; the recommendation is a plain highlighted card, not a chat bubble — it's a static suggestion, not a conversation.

## 9. History page

```
Date | Item | Category | Amount | CO2e | Method | [Edit] [Delete]
```

Edit reopens the same field-level form used during verification; delete asks for a single confirm ("Remove this transaction?") and nothing more elaborate.

## 10. Error / empty states

| Situation | What's shown |
|---|---|
| No transactions yet | Dashboard shows "No data yet — upload a bill, import a CSV, or add an entry" instead of empty charts |
| CSV missing a required column | Inline error naming the missing column before any preview is shown |
| Unreadable/empty upload | "Couldn't read this file — try manual entry instead" with a direct link to the manual form |
| Category not recognized | Falls back to "Other" and is visibly flagged as auto-assigned, inviting a manual fix |
