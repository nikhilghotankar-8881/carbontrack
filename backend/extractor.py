import os
import re
from datetime import datetime
import pymupdf as fitz
from PIL import Image
import pytesseract


def extract_text_from_pdf(pdf_stream_or_path) -> str:
    """Extracts text directly from a text-based PDF using PyMuPDF."""
    text = ""
    try:
        if isinstance(pdf_stream_or_path, (str, bytes)):
            doc = fitz.open(pdf_stream_or_path)
        else:
            doc = fitz.open(stream=pdf_stream_or_path.read(), filetype="pdf")
            pdf_stream_or_path.seek(0)

        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception:
        text = ""
    return text.strip()


def extract_text_from_image(image_file_or_path) -> str:
    """Extracts text from an image (JPG/PNG/Scanned PDF) using Tesseract OCR."""
    text = ""
    try:
        if isinstance(image_file_or_path, str):
            image = Image.open(image_file_or_path)
        else:
            image = Image.open(image_file_or_path)
            image_file_or_path.seek(0)

        text = pytesseract.image_to_string(image)
    except Exception:
        text = ""
    return text.strip()


def process_document_file(file_obj, filename: str, document_type: str = "electricity_bill") -> dict:
    """
    Main extraction function for bill/invoice files (PDF, JPG, PNG).
    Tries PyMuPDF text extraction first; falls back to Tesseract OCR if text is empty.
    Parses document type specific fields.
    """
    ext = os.path.splitext(filename)[1].lower()
    raw_text = ""

    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_obj)
        if len(raw_text) < 20:
            try:
                doc = fitz.open(stream=file_obj.read(), filetype="pdf")
                file_obj.seek(0)
                ocr_text = ""
                for page in doc:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text += pytesseract.image_to_string(img) + "\n"
                doc.close()
                if len(ocr_text) > len(raw_text):
                    raw_text = ocr_text
            except Exception:
                pass
    elif ext in [".jpg", ".jpeg", ".png"]:
        raw_text = extract_text_from_image(file_obj)

    if document_type == "electricity_bill":
        parsed = parse_electricity_bill_text(raw_text)
    else:
        parsed = parse_shopping_invoice_text(raw_text)

    parsed["raw_text"] = raw_text
    return parsed


def parse_electricity_bill_text(text: str) -> dict:
    """
    Parses raw extracted text from an electricity bill.
    Target fields: consumer_name, bill_date, units_consumed, bill_amount.
    """
    fields = {
        "consumer_name": "",
        "bill_date": datetime.today().strftime("%Y-%m-%d"),
        "units_consumed": 0.0,
        "bill_amount": 0.0
    }

    if not text:
        return fields

    # 1. Bill Date extraction
    date_match = re.search(r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b', text)
    if date_match:
        d_str = date_match.group(1)
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                dt = datetime.strptime(d_str, fmt)
                fields["bill_date"] = dt.strftime("%Y-%m-%d")
                break
            except ValueError:
                continue

    # 2. Bill Amount extraction (e.g., Total: 1640.00, Rs. 1640, ₹1640)
    amt_match = re.search(r'(?:total|amount|payable|bill amount|net amount|rs\.?|inr|₹)\s*:?\s*([0-9,]+(?:\.[0-9]{2})?)', text, re.IGNORECASE)
    if amt_match:
        try:
            amt_clean = amt_match.group(1).replace(",", "")
            fields["bill_amount"] = float(amt_clean)
        except ValueError:
            pass

    # 3. Units Consumed (kWh) extraction
    units_pattern = r'\b(kwh|units|unit)\b'
    for line in text.splitlines():
        q_match = re.search(r'\b([0-9]+(?:\.[0-9]+)?)\s*' + units_pattern, line, re.IGNORECASE)
        if not q_match:
            q_match_rev = re.search(units_pattern + r'\s*(?:consumed|used|qty|quantity)?\s*:?\s*([0-9]+(?:\.[0-9]+)?)', line, re.IGNORECASE)
            if q_match_rev:
                fields["units_consumed"] = float(q_match_rev.group(2))
                break
        else:
            fields["units_consumed"] = float(q_match.group(1))
            break

    # 4. Consumer Name heuristics
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if re.search(r'consumer name|name|customer|account name', line, re.IGNORECASE):
            parts = line.split(":", 1)
            if len(parts) > 1 and len(parts[1].strip()) > 2:
                fields["consumer_name"] = parts[1].strip()
                break

    if not fields["consumer_name"] and lines:
        for line in lines[:5]:
            if len(line) < 40 and not re.search(r'bill|invoice|total|electricity|power|bescom|mseb|tneb|page', line, re.I):
                fields["consumer_name"] = line
                break

    return fields


def parse_shopping_invoice_text(text: str) -> dict:
    """
    Parses raw extracted text from a shopping invoice.
    Target fields: product_name, quantity, amount, date.
    """
    fields = {
        "product_name": "",
        "quantity": 1.0,
        "amount": 0.0,
        "date": datetime.today().strftime("%Y-%m-%d")
    }

    if not text:
        return fields

    # 1. Date extraction
    date_match = re.search(r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b', text)
    if date_match:
        d_str = date_match.group(1)
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                dt = datetime.strptime(d_str, fmt)
                fields["date"] = dt.strftime("%Y-%m-%d")
                break
            except ValueError:
                continue

    # 2. Amount extraction
    amt_match = re.search(r'(?:total|amount|grand total|net amount|paid|rs\.?|inr|₹)\s*:?\s*([0-9,]+(?:\.[0-9]{2})?)', text, re.IGNORECASE)
    if amt_match:
        try:
            amt_clean = amt_match.group(1).replace(",", "")
            fields["amount"] = float(amt_clean)
        except ValueError:
            pass

    # 3. Quantity extraction
    qty_match = re.search(r'(?:qty|quantity|items|pcs)\s*:?\s*([0-9]+)', text, re.IGNORECASE)
    if qty_match:
        try:
            fields["quantity"] = float(qty_match.group(1))
        except ValueError:
            pass

    # 4. Product Name heuristics
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if re.search(r'item|product|description|particulars', line, re.IGNORECASE):
            parts = line.split(":", 1)
            if len(parts) > 1 and len(parts[1].strip()) > 2:
                fields["product_name"] = parts[1].strip()
                break

    if not fields["product_name"] and lines:
        for line in lines:
            if not re.search(r'invoice|tax|total|subtotal|date|order|gst|shipping|payment|amount|bill|rs|inr', line, re.I) and len(line) > 3:
                fields["product_name"] = line
                break

    return fields
