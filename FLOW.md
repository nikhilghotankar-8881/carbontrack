# Flow

*All pipelines the prototype actually runs. For what each stage's code lives in, see `ARCHITECTURE.md`; for field names, see `PARAMETERS.md`.*

## 1. Master Pipeline (both inputs converge here)

```
ELECTRICITY BILL              ONLINE SHOPPING INVOICE
       |                               |
       +-------------------------------+
                       |
                    UPLOAD
                       |
               OCR / TEXT EXTRACTION
                       |
               STRUCTURED DATA
                       |
            HUMAN VERIFICATION (mandatory)
                       |
              CATEGORY DETECTION
                       |
           EMISSION FACTOR SELECTION
                       |
         +-------------+-------------+
         |                           |
 ACTIVITY DATA AVAILABLE      ONLY ₹ VALUE KNOWN
         |                           |
 ACTIVITY-BASED CALC         SPEND-BASED CALC
         |                           |
         +-------------+-------------+
                       |
                ESTIMATED CO₂e
                       |
              SAVE CALCULATION
              (with full metadata)
                       |
                   DASHBOARD
                       |
         TODAY + MONTHLY + CATEGORY
```

## 2. Electricity Bill Flow (Phase 7)

```
Upload Electricity Bill (PDF / JPG / PNG)
                |
Does the PDF already contain text?
   |Yes                     |No / image file
   |                         |
Extract text directly      Run Tesseract OCR
   |                         |
   +-----------+-------------+
               |
    Parse fields from raw text:
    - Consumer Name
    - Bill Date
    - Units Consumed (kWh)
    - Amount (₹)
               |
    Show "Verify Extracted Information"
    form with every field editable
               |
         User Confirms
               |
    Category = Electricity
               |
    Activity = 240 kWh
               |
    Find CEA Factor (from emission_factors table)
               |
    Calculate: 240 × factor = XXX kg CO₂e
               |
    Save Calculation (with activity, factor, source, version, method)
               |
    Show Result:
    - XXX kg CO₂e
    - Method: Activity-based
    - Factor: XXX kg CO₂e/kWh
    - Source: Central Electricity Authority
    - Version: XXX
```

## 3. Online Shopping Invoice Flow (Phase 8)

```
Upload Shopping Invoice (PDF / JPG / PNG)
                |
    OCR / Text Extraction
                |
    Extract fields:
    - Product Name (e.g. Cotton T-Shirt)
    - Quantity (e.g. 1)
    - Amount (e.g. ₹799)
    - Date (e.g. 30/09/2026)
                |
    Show Verification Form
    (all fields editable)
                |
    User Confirms
                |
    Category Detection:
    Cotton T-Shirt → Clothing
                |
    Emission Factor Selection:
    Clothing → spend/category factor
                |
    Spend-based Calculation:
    ₹799 × category factor = XX kg CO₂e
                |
    Save Calculation
                |
    Show Result:
    - Product: Cotton T-Shirt
    - Category: Clothing
    - Quantity: 1
    - Purchase Value: ₹799
    - Method: Category/Spend-based
    - Estimated Carbon: XX kg CO₂e
    - Source: XXXXXXXX
```

## 4. Categorization + Factor Mapping Flow (Phase 6)

```
Confirmed Extracted Data
          |
    Category Detection (rule-based):
    - electricity → Electricity
    - petrol → Fuel
    - diesel → Fuel
    - rice → Food
    - milk → Food
    - shirt → Clothing
    - mobile → Electronics
    - (no match) → Other
          |
    Emission Factor Selection:
    Category + Unit → Look up factor from emission_factors table
          |
    Return:
    - Category
    - Unit
    - Emission Factor value
    - Source
    - Version
```

## 5. Calculation Decision Flow

```
Is a physical quantity known (kWh, litres, kg)?
        |Yes                          |No
        |                              |
Activity-based:                 Spend-based:
CO₂e = quantity × factor        CO₂e = amount × category factor
        |                              |
Returns:                        Returns:
- activity_value                - activity_value (₹ amount)
- activity_unit                 - activity_unit (INR)
- factor_value                  - factor_value
- factor_unit                   - factor_unit
- result_co2e                   - result_co2e
- method: activity-based        - method: spend-based
- source                        - source
- version                       - version
```

## 6. "How Was This Calculated?" Flow (Phase 11)

```
User clicks "How was this calculated?" on any record
          |
    Retrieve saved calculation metadata:
          |
    For Electricity:
    INPUT: 240 kWh
        ↓
    EMISSION FACTOR: XXX kg CO₂e/kWh
        ↓
    FORMULA: 240 × XXX
        ↓
    RESULT: XXX kg CO₂e
        ↓
    SOURCE: CEA

    For Shopping:
    INPUT: ₹799
        ↓
    CATEGORY: Clothing
        ↓
    CATEGORY FACTOR: XXX
        ↓
    FORMULA: Spend-based calculation
        ↓
    RESULT: XX kg CO₂e
```

## 7. Dashboard Aggregation Flow (Phase 10)

```
All saved calculations
          |
    Group by date → Today's CO₂e total
    Group by month → This Month's CO₂e total
    Group by category → Category breakdown
          |
    Render:
    - Today: XXX kg CO₂e
    - This Month: XXX kg CO₂e
    - Electricity: XX kg
    - Shopping: XX kg
    - Food: XX kg
    - Fuel: XX kg
    - Recent calculations list
```

## 8. Error Handling Flow (Phase 12)

```
Upload document
        |
    Is it a supported format (PDF/JPG/PNG)?
        |No → "Unsupported document type"
        |Yes
        |
    Can OCR read it?
        |No → "Unable to read this document. Please try a clearer image."
        |Yes
        |
    Are required fields extracted?
        |Missing → Fields left blank/highlighted, user fills manually
        |Yes
        |
    Verification form shown
        |
    Is category recognized?
        |No → Falls back to "Other", flagged for user
        |Yes
        |
    Proceed to calculation
```
