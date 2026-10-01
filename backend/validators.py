from datetime import datetime
import pandas as pd

ALLOWED_CATEGORIES = {
    "Electricity", "Fuel", "Transport", "Grocery", 
    "Clothing", "Electronics", "Household", "Other"
}

ALLOWED_FILE_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


def validate_file_extension(filename: str) -> tuple[bool, str]:
    """Validates if file extension is allowed."""
    ext = str(filename).strip().lower()[str(filename).rfind('.'):] if '.' in filename else ''
    if ext in ALLOWED_FILE_EXTENSIONS:
        return True, ""
    return False, f"File format '{ext}' is not supported. Please upload PDF, JPG, or PNG."


def validate_date(date_str: str) -> tuple[bool, str]:
    """Validates date string in YYYY-MM-DD format."""
    if not date_str:
        return False, "Date cannot be empty."
    try:
        datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
        return True, str(date_str).strip()
    except ValueError:
        try:
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
    """Validates physical quantity (optional, but must be >= 0 if provided)."""
    if quantity is None or str(quantity).strip() == "":
        return True, None, ""
    try:
        val = float(quantity)
        if val < 0:
            return False, 0.0, "Quantity cannot be negative."
        return True, val, ""
    except (ValueError, TypeError):
        return False, 0.0, "Quantity must be a valid number."


def validate_category(category: str) -> tuple[bool, str]:
    """Validates if category is in the allowed list."""
    if category in ALLOWED_CATEGORIES:
        return True, ""
    return False, f"Category '{category}' is invalid. Must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}"
