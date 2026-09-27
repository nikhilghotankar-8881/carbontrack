from modules.database import get_emission_factor

def calculate_activity_emission(quantity: float, unit: str, category: str, item: str = None) -> dict:
    """
    Calculates CO2e emission using the activity-based method (quantity * factor).
    Looks up emission factor from DB.
    Returns dictionary with calculated co2e and factor metadata.
    """
    if quantity is None or quantity < 0:
        raise ValueError("Quantity must be a non-negative number for activity-based calculation.")
        
    factor_row = get_emission_factor(category=category, method="activity", activity=item)
    if not factor_row:
        # Fallback to spend-based if activity factor not found for category
        raise ValueError(f"No activity-based emission factor found for category '{category}' and item '{item}'.")

    factor_value = float(factor_row['factor'])
    co2e = round(quantity * factor_value, 4)

    return {
        "co2e": co2e,
        "calculation_method": "activity-based",
        "factor_used": factor_value,
        "unit_used": factor_row['unit'],
        "source": factor_row['source'],
        "source_year": factor_row['source_year'],
        "data_quality": "High"
    }

def calculate_spend_emission(amount: float, category: str) -> dict:
    """
    Calculates CO2e emission using the spend-based method (amount * spend_factor).
    Looks up spend-based factor from DB.
    Returns dictionary with calculated co2e and factor metadata.
    """
    if amount is None or amount < 0:
        raise ValueError("Amount must be a non-negative number for spend-based calculation.")

    factor_row = get_emission_factor(category=category, method="spend")
    if not factor_row:
        # Fallback to Other spend factor if specific category spend factor not found
        factor_row = get_emission_factor(category="Other", method="spend")

    if not factor_row:
        raise ValueError(f"No spend-based emission factor available for category '{category}'.")

    factor_value = float(factor_row['factor'])
    co2e = round(amount * factor_value, 4)

    return {
        "co2e": co2e,
        "calculation_method": "spend-based",
        "factor_used": factor_value,
        "unit_used": factor_row['unit'],
        "source": factor_row['source'],
        "source_year": factor_row['source_year'],
        "data_quality": "Medium"
    }

def calculate_total_emission(transactions: list) -> float:
    """
    Calculates total CO2e from a list of transaction dicts or DataFrame rows.
    """
    if not transactions:
        return 0.0
    
    total = 0.0
    for t in transactions:
        if isinstance(t, dict):
            total += t.get('co2e', 0.0)
        elif hasattr(t, 'co2e'):
            total += getattr(t, 'co2e', 0.0)
    return round(total, 4)
