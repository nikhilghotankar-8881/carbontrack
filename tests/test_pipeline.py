import pytest
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.database import init_db, save_transaction, get_all_transactions
from modules.calculator import calculate_activity_emission, calculate_spend_emission
from modules.classifier import classify_text
from modules.extractor import parse_receipt_text
from modules.recommendations import get_recommendation_for_category
from modules.validators import validate_csv_columns, validate_amount, validate_date

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_classifier_accuracy():
    assert classify_text("Cotton T-Shirt") == "Clothing"
    assert classify_text("Wireless Earbuds") == "Electronics"
    assert classify_text("HPCL Petrol Fill") == "Fuel"
    assert classify_text("BigBasket Grocery") == "Food"
    assert classify_text("Uber Cab") == "Transport"
    assert classify_text("Unrecognized Mystery Item") == "Other"

def test_receipt_parsing():
    text = "BESCOM Electricity Bill\nDate: 2026-09-15\nUnits Consumed: 185 kWh\nTotal Amount: Rs. 1640.00"
    parsed = parse_receipt_text(text)
    assert parsed["date"] == "2026-09-15"
    assert parsed["item"] == "Electricity Bill"
    assert parsed["quantity"] == 185.0
    assert parsed["unit"] == "kwh"
    assert parsed["amount"] == 1640.0

def test_unified_pipeline_manual_csv_bill():
    # 1. Manual Entry
    res_m = calculate_activity_emission(185, "kWh", "Electricity")
    tx_m = {
        "date": "2026-09-25",
        "vendor": "BESCOM",
        "item": "Electricity Bill",
        "category": "Electricity",
        "amount": 1640.0,
        "quantity": 185.0,
        "unit": "kWh",
        "co2e": res_m["co2e"],
        "calculation_method": res_m["calculation_method"],
        "source_type": "manual"
    }
    save_transaction(tx_m)

    # 2. CSV Purchase Entry
    res_c = calculate_spend_emission(799.0, "Clothing")
    tx_c = {
        "date": "2026-09-26",
        "vendor": "Amazon",
        "item": "Cotton T-Shirt",
        "category": "Clothing",
        "amount": 799.0,
        "quantity": None,
        "unit": None,
        "co2e": res_c["co2e"],
        "calculation_method": res_c["calculation_method"],
        "source_type": "csv"
    }
    save_transaction(tx_c)

    # 3. Bill Receipt Entry
    res_b = calculate_activity_emission(10.0, "litre", "Fuel", item="Petrol")
    tx_b = {
        "date": "2026-09-27",
        "vendor": "HPCL",
        "item": "Petrol Fill",
        "category": "Fuel",
        "amount": 1000.0,
        "quantity": 10.0,
        "unit": "litre",
        "co2e": res_b["co2e"],
        "calculation_method": res_b["calculation_method"],
        "source_type": "bill"
    }
    save_transaction(tx_b)

    # Retrieve all
    df = get_all_transactions()
    assert len(df) >= 3
    assert set(df['source_type'].unique()).issuperset({"manual", "csv", "bill"})
    assert set(df['calculation_method'].unique()).issuperset({"activity-based", "spend-based"})

def test_recommendation_engine():
    rec_elec = get_recommendation_for_category("Electricity")
    assert "Electricity" in rec_elec or "lighting" in rec_elec
    rec_fuel = get_recommendation_for_category("Fuel")
    assert "Fuel" in rec_fuel or "errands" in rec_fuel

def test_validators():
    valid, msg = validate_csv_columns(pd.DataFrame(columns=["date", "vendor", "product", "amount"]))
    assert valid is True
    valid_d, d_str = validate_date("2026-09-27")
    assert valid_d is True
    assert d_str == "2026-09-27"
    valid_a, amt, _ = validate_amount("1500")
    assert valid_a is True
    assert amt == 1500.0
