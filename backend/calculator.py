from database.db import get_emission_factor


def calculate_activity_emission(quantity: float, unit: str, category: str, item: str = None) -> dict:
    """
    Calculates CO2e emission using the activity-based method (quantity * factor).
    Looks up emission factor from DB.
    Returns dictionary with calculated result_co2e and factor metadata.
    """
    if quantity is None or quantity < 0:
        raise ValueError("Quantity must be a non-negative number for activity-based calculation.")

    factor_row = get_emission_factor(category=category, method="activity-based", unit=unit, activity=item)
    if not factor_row:
        raise ValueError(f"No activity-based emission factor found for category '{category}', unit '{unit}', item '{item}'.")

    factor_value = float(factor_row['factor_value'])
    co2e = round(quantity * factor_value, 4)

    return {
        "activity_value": quantity,
        "activity_unit": unit,
        "factor_id": factor_row['id'],
        "factor_value": factor_value,
        "factor_unit": factor_row['factor_unit'],
        "result_co2e": co2e,
        "co2e": co2e,
        "method": "activity-based",
        "source": factor_row['source'],
        "version": factor_row['version'],
        "source_url": factor_row.get('source_url', ''),
        "category": category
    }


def calculate_spend_emission(amount: float, category: str) -> dict:
    """
    Calculates CO2e emission using the spend-based method (amount * spend_factor).
    Looks up spend-based factor from DB (unit = 'INR').
    Returns dictionary with calculated result_co2e and factor metadata.
    """
    if amount is None or amount < 0:
        raise ValueError("Amount must be a non-negative number for spend-based calculation.")

    factor_row = get_emission_factor(category=category, method="spend-based")
    if not factor_row:
        factor_row = get_emission_factor(category="Other", method="spend-based")

    if not factor_row:
        raise ValueError(f"No spend-based emission factor available for category '{category}'.")

    factor_value = float(factor_row['factor_value'])
    co2e = round(amount * factor_value, 4)

    return {
        "activity_value": amount,
        "activity_unit": "INR",
        "factor_id": factor_row['id'],
        "factor_value": factor_value,
        "factor_unit": factor_row['factor_unit'],
        "result_co2e": co2e,
        "co2e": co2e,
        "method": "spend-based",
        "source": factor_row['source'],
        "version": factor_row['version'],
        "source_url": factor_row.get('source_url', ''),
        "category": category
    }


def calculate_total_emission(calculations: list) -> float:
    """
    Calculates total CO2e from a list of calculation dicts or DataFrame rows.
    """
    if not calculations:
        return 0.0

    total = 0.0
    for calc in calculations:
        if isinstance(calc, dict):
            val = calc.get('result_co2e') if 'result_co2e' in calc else calc.get('co2e', 0.0)
            total += val or 0.0
        elif hasattr(calc, 'result_co2e'):
            total += getattr(calc, 'result_co2e', 0.0)
        elif hasattr(calc, 'co2e'):
            total += getattr(calc, 'co2e', 0.0)
    return round(total, 4)
