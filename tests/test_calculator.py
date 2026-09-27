import pytest
import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.database import init_db
from modules.calculator import (
    calculate_activity_emission,
    calculate_spend_emission,
    calculate_total_emission
)

@pytest.fixture(autouse=True)
def setup_database():
    """Ensure database is initialized before tests run."""
    init_db()

def test_activity_electricity():
    res = calculate_activity_emission(185, "kWh", "Electricity")
    assert res["co2e"] == pytest.approx(132.46, abs=0.01)
    assert res["calculation_method"] == "activity-based"
    assert res["data_quality"] == "High"

def test_activity_petrol():
    res = calculate_activity_emission(10, "litre", "Fuel", item="Petrol")
    assert res["co2e"] == pytest.approx(23.10, abs=0.01)
    assert res["calculation_method"] == "activity-based"
    assert res["data_quality"] == "High"

def test_activity_diesel():
    res = calculate_activity_emission(5, "litre", "Fuel", item="Diesel")
    assert res["co2e"] == pytest.approx(13.40, abs=0.01)

def test_activity_lpg():
    res = calculate_activity_emission(14.2, "kg", "Fuel", item="LPG")
    assert res["co2e"] == pytest.approx(42.316, abs=0.01)

def test_spend_clothing():
    res = calculate_spend_emission(799, "Clothing")
    assert res["co2e"] == pytest.approx(6.392, abs=0.01)
    assert res["calculation_method"] == "spend-based"
    assert res["data_quality"] == "Medium"

def test_spend_food():
    res = calculate_spend_emission(650, "Food")
    assert res["co2e"] == pytest.approx(9.75, abs=0.01)

def test_spend_electronics():
    res = calculate_spend_emission(1499, "Electronics")
    assert res["co2e"] == pytest.approx(7.495, abs=0.01)

def test_total_emission_calculation():
    txs = [
        {"co2e": 132.46},
        {"co2e": 6.392},
        {"co2e": 9.75}
    ]
    total = calculate_total_emission(txs)
    assert total == pytest.approx(148.602, abs=0.01)

def test_total_emission_empty():
    assert calculate_total_emission([]) == 0.0

def test_negative_quantity_raises():
    with pytest.raises(ValueError):
        calculate_activity_emission(-10, "kWh", "Electricity")

def test_negative_amount_raises():
    with pytest.raises(ValueError):
        calculate_spend_emission(-100, "Food")
