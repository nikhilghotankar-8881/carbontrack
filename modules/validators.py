import re
from datetime import datetime
import pandas as pd

ALLOWED_CATEGORIES = {
    "Electricity", "Fuel", "Transport", "Food", 
    "Clothing", "Electronics", "Household", "Other"
}

ALLOWED_FILE_EXTENSIONS = {
    "bill": {".pdf", ".jpg", ".jpeg", ".png"},
    "csv": {".csv"}
}

REQUIRED_CSV_COLUMNS = {"date", "vendor", "product", "amount"}

def validate_csv_columns(df: pd.DataFrame) -> tuple[bool, str]:
    """Validates if CSV contains all required columns."""
    df_cols = set(col.strip().lower() for col in df.columns)
    missing = REQUIRED_CSV_COLUMNS - df_cols
    if missing:
        return False, f"Missing required columns in CSV: {', '.join(sorted(missing))}"
    return True, ""

def validate_date(date_str: str) -> tuple[bool, str]:
    """Validates date string in YYYY-MM-DD format."""
    if not date_str:
        return False, "Date cannot be empty."
    try:
        datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
        return True, str(date_str).strip()
    except ValueError:
        try:
            # Try alternate common date formats
            for fmt in ("%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
                try:
                    dt = datetime.strptime(str(date_str).strip(), fmt)
                    return True, dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        except Exception:
            pass
        return False, f"Invalid date format '{date_str}'. Expected YYYY-MM-DD."

def validate_amount(amount) -> tuple[bool, float, str]:
    """Validates numeric non-negative currency amount."""
    try:
        val = float(amount)
        if val < 0:
            return False, 0.0, "Amount cannot be negative."
        return True, val, ""
    except (ValueError, TypeError):
        return False, 0.0, "Amount must be a valid number."

def validate_quantity(quantity) -> tuple[bool, float, str]:
    """Validates physical quantity (optional, but must be >0 if provided)."""
    if quantity is None or str(quantity).strip() == "":
        return True, None, ""
    try:
        val = float(quantity)
        if val <= 0:
            return False, 0.0, "Quantity must be greater than zero."
        return True, val, ""
    except (ValueError, TypeError):
        return False, 0.0, "Quantity must be a valid number."

def validate_category(category: str) -> tuple[bool, str]:
    """Validates if category is in the locked list of 8 categories."""
    if category in ALLOWED_CATEGORIES:
        return True, ""
    return False, f"Category '{category}' is invalid. Must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}"
