import os
import sys
import pytest

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import init_db
from backend.calculator import (
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
    assert res["result_co2e"] == pytest.approx(134.495, abs=0.01)
    assert res["method"] == "activity-based"
    assert res["source"] == "Central Electricity Authority (CEA)"
    assert res["version"] == "v20.0"


def test_activity_petrol():
    res = calculate_activity_emission(10, "litre", "Fuel", item="Petrol")
    assert res["result_co2e"] == pytest.approx(21.60, abs=0.01)
    assert res["method"] == "activity-based"


def test_activity_diesel():
    res = calculate_activity_emission(5, "litre", "Fuel", item="Diesel")
    assert res["result_co2e"] == pytest.approx(13.40, abs=0.01)


def test_activity_lpg():
    res = calculate_activity_emission(14.2, "kg", "Fuel", item="LPG")
    assert res["result_co2e"] == pytest.approx(42.316, abs=0.01)


def test_spend_clothing():
    res = calculate_spend_emission(799, "Clothing")
    assert res["result_co2e"] == pytest.approx(6.392, abs=0.01)
    assert res["method"] == "spend-based"


def test_spend_grocery():
    res = calculate_spend_emission(650, "Grocery")
    assert res["result_co2e"] == pytest.approx(9.75, abs=0.01)


def test_spend_electronics():
    res = calculate_spend_emission(1499, "Electronics")
    assert res["result_co2e"] == pytest.approx(7.495, abs=0.01)


def test_total_emission_calculation():
    calcs = [
        {"result_co2e": 134.495},
        {"result_co2e": 6.392},
        {"result_co2e": 9.75}
    ]
    total = calculate_total_emission(calcs)
    assert total == pytest.approx(150.637, abs=0.01)


def test_total_emission_empty():
    assert calculate_total_emission([]) == 0.0


def test_negative_quantity_raises():
    with pytest.raises(ValueError):
        calculate_activity_emission(-10, "kWh", "Electricity")


def test_negative_amount_raises():
    with pytest.raises(ValueError):
        calculate_spend_emission(-100, "Grocery")
