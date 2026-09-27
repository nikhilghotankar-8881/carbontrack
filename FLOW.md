# Flow

*All pipelines the prototype actually runs. For what each stage's code lives in, see `ARCHITECTURE.md`; for field names, see `PARAMETERS.md`.*

## 1. Master pipeline (all inputs converge here)

```
BILL / RECEIPT       ONLINE PURCHASE CSV       MANUAL ENTRY
      |                       |                      |
      +-----------------------+----------------------+
                              |
                       DATA EXTRACTION
                              |
                      USER VERIFICATION
                              |
                       CLASSIFICATION
                              |
                  EMISSION FACTOR LOOKUP
                              |
              +---------------+----------------+
              |                                |
     ACTIVITY DATA AVAILABLE            ONLY ₹ VALUE KNOWN
              |                                |
     ACTIVITY-BASED CALC              SPEND-BASED CALC
              |                                |
              +---------------+----------------+
                              |
                        ESTIMATED CO2e
                              |
                       STORE TRANSACTION
                              |
                          DASHBOARD
                              |
              TOTAL + DAILY/MONTHLY + CATEGORY
                              |
                     ONE SIMPLE SUGGESTION
```

## 2. Bill/receipt extraction flow

```
Upload PDF / JPG / PNG
        |
Does the PDF already contain text?
   |Yes                    |No / image file
   |                        |
Extract text directly     Run Tesseract OCR
   |                        |
   +-----------+------------+
               |
     Parse fields: date, vendor,
     item, quantity, unit, amount
               |
   Show "Verify extracted information"
   form with every field editable
               |
        User confirms
               |
        Proceeds to classification
```

Real receipts have inconsistent layouts, so extraction never writes straight to the database — the verification step is mandatory, not optional.

## 3. Online purchase CSV flow

```
Upload CSV (date, vendor, product, amount)
               |
      Validate required columns
               |
   Classify each product → category
               |
   Show preview table before saving:
   Date | Product | Category | Amount
               |
         User clicks "Confirm Import"
               |
   Apply spend-based factor per row
               |
        Save each row as a transaction
```

## 4. Manual entry flow

```
Form: Date, Category, Item, Amount, Quantity, Unit
               |
           Validation
               |
   Category already chosen by user (no classifier needed)
               |
        Emission factor lookup
               |
             CO2e
               |
          Save to SQLite
```

## 5. Calculation decision flow

```
Is a physical quantity known (kWh, litres, kg, km)?
        |Yes                          |No
        |                             |
Activity-based:                Spend-based:
CO2e = quantity × factor       CO2e = amount × category factor
        |                             |
Data quality: High            Data quality: Medium
```

## 6. Dashboard aggregation flow

```
All saved transactions
         |
   Group by date -> Daily CO2e
   Group by month -> Monthly CO2e
   Group by category -> Category breakdown
         |
   Category with max CO2e = Highest contributor
         |
   Look up matching rule in recommendations.py
         |
   Render KPI cards + charts + recommendation text
```

## 7. Edit/delete flow (History page)

```
User opens History
         |
   Table of all past transactions
         |
   Edit -> reopen the same verification-style form -> re-save
   Delete -> remove row -> dashboard totals recalculate on next load
```
