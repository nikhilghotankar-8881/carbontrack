import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import init_db, save_document, save_calculation, get_all_calculations
from backend.calculator import calculate_activity_emission, calculate_spend_emission
from backend.classifier import classify_text
from backend.extractor import parse_electricity_bill_text, parse_shopping_invoice_text
from backend.validators import validate_amount, validate_date, validate_file_extension


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_classifier_accuracy():
    assert classify_text("Cotton T-Shirt") == "Clothing"
    assert classify_text("Wireless Earbuds") == "Electronics"
    assert classify_text("HPCL Petrol Fill") == "Fuel"
    assert classify_text("BigBasket Grocery") == "Grocery"
    assert classify_text("Unrecognized Mystery Item") == "Other"


def test_electricity_bill_parsing():
    text = "BESCOM Electricity Bill\nConsumer Name: John Doe\nDate: 2026-09-15\nUnits Consumed: 185 kWh\nTotal Amount: Rs. 1640.00"
    parsed = parse_electricity_bill_text(text)
    assert parsed["bill_date"] == "2026-09-15"
    assert parsed["units_consumed"] == 185.0
    assert parsed["bill_amount"] == 1640.0


def test_shopping_invoice_parsing():
    text = "Amazon Shopping Invoice\nItem: Cotton T-Shirt\nDate: 2026-09-26\nQty: 1\nTotal: INR 799.00"
    parsed = parse_shopping_invoice_text(text)
    assert parsed["date"] == "2026-09-26"
    assert parsed["amount"] == 799.0


def test_unified_pipeline_bill_and_invoice():
    # 1. Electricity Bill Entry
    doc_id_1 = save_document("electricity_bill.pdf", "pdf", "electricity_bill", "raw text content")
    res_b = calculate_activity_emission(185, "kWh", "Electricity")
    calc_1 = {
        "document_id": doc_id_1,
        "date": "2026-09-25",
        "category": "Electricity",
        "activity_value": 185.0,
        "activity_unit": "kWh",
        "factor_id": res_b["factor_id"],
        "factor_value": res_b["factor_value"],
        "method": res_b["method"],
        "source": res_b["source"],
        "version": res_b["version"],
        "result_co2e": res_b["result_co2e"]
    }
    save_calculation(calc_1)

    # 2. Shopping Invoice Entry
    doc_id_2 = save_document("shopping_invoice.pdf", "pdf", "shopping_invoice", "raw text content")
    res_s = calculate_spend_emission(799.0, "Clothing")
    calc_2 = {
        "document_id": doc_id_2,
        "date": "2026-09-26",
        "category": "Clothing",
        "activity_value": 799.0,
        "activity_unit": "INR",
        "factor_id": res_s["factor_id"],
        "factor_value": res_s["factor_value"],
        "method": res_s["method"],
        "source": res_s["source"],
        "version": res_s["version"],
        "result_co2e": res_s["result_co2e"]
    }
    save_calculation(calc_2)

    df = get_all_calculations()
    assert len(df) >= 2
    assert set(df['method'].unique()).issuperset({"activity-based", "spend-based"})


def test_validators():
    valid_ext, _ = validate_file_extension("bill.pdf")
    assert valid_ext is True
    valid_d, d_str = validate_date("2026-09-27")
    assert valid_d is True
    assert d_str == "2026-09-27"
    valid_a, amt, _ = validate_amount("1500")
    assert valid_a is True
    assert amt == 1500.0
