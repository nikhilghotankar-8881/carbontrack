import os
import re
from datetime import datetime
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

def extract_text_from_pdf(pdf_stream_or_path) -> str:
    """Extracts text directly from a text-based PDF using PyMuPDF."""
    text = ""
    try:
        if isinstance(pdf_stream_or_path, (str, bytes)):
            doc = fitz.open(pdf_stream_or_path)
        else:
            # Stream from Streamlit file uploader
            doc = fitz.open(stream=pdf_stream_or_path.read(), filetype="pdf")
            pdf_stream_or_path.seek(0)  # Reset stream position

        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
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
    except Exception as e:
        text = ""
    return text.strip()

def process_bill_file(file_obj, filename: str) -> dict:
    """
    Main extraction function for bill/receipt files (PDF, JPG, PNG).
    Tries PyMuPDF text extraction first; falls back to Tesseract OCR if text is empty.
    Parses date, vendor, item, quantity, unit, amount using regex heuristics.
    """
    ext = os.path.splitext(filename)[1].lower()
    raw_text = ""
    
    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_obj)
        # If text PDF extraction returned empty/sparse text, attempt OCR via PyMuPDF image render
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

    parsed_fields = parse_receipt_text(raw_text)
    parsed_fields["raw_text"] = raw_text
    return parsed_fields

def parse_receipt_text(text: str) -> dict:
    """
    Parses raw extracted text from a bill/receipt using heuristics and regex.
    Returns dictionary with extracted fields: date, vendor, item, quantity, unit, amount.
    """
    fields = {
        "date": None,
        "vendor": None,
        "item": None,
        "quantity": None,
        "unit": None,
        "amount": None
    }

    if not text:
        return fields

    # 1. Date extraction (formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, DD Mon YYYY)
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

    # 2. Amount extraction (e.g. Total: 1640.00, Rs. 1640, INR 1640, ₹1640)
    amt_match = re.search(r'(?:total|amount|net|paid|rs\.?|inr|₹)\s*:?\s*([0-9,]+(?:\.[0-9]{2})?)', text, re.IGNORECASE)
    if amt_match:
        try:
            amt_clean = amt_match.group(1).replace(",", "")
            fields["amount"] = float(amt_clean)
        except ValueError:
            pass

    # 3. Quantity and Unit extraction (e.g. 185 kWh, 10 litres, 14.2 kg)
    qty_unit_match = re.search(r'(\d+(?:\.\d+)?)\s*(kwh|unit|units|litre|litres|liter|liters|kg|lpg)', text, re.IGNORECASE)
    if qty_unit_match:
        try:
            fields["quantity"] = float(qty_unit_match.group(1))
            fields["unit"] = qty_unit_match.group(2).lower()
        except ValueError:
            pass

    # 4. Vendor extraction heuristics
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        # First non-empty line is often the vendor name
        first_line = lines[0]
        if len(first_line) < 40 and not re.search(r'receipt|bill|invoice|total', first_line, re.I):
            fields["vendor"] = first_line

    # 5. Item description heuristics
    if "electricity" in text.lower() or "kwh" in text.lower():
        fields["item"] = "Electricity Bill"
        if not fields["unit"]:
            fields["unit"] = "kWh"
    elif "petrol" in text.lower() or "fuel" in text.lower():
        fields["item"] = "Petrol Fill"
        if not fields["unit"]:
            fields["unit"] = "litre"
    elif "diesel" in text.lower():
        fields["item"] = "Diesel Fill"
        if not fields["unit"]:
            fields["unit"] = "litre"
    elif "lpg" in text.lower() or "gas cylinder" in text.lower():
        fields["item"] = "LPG Cylinder"
        if not fields["unit"]:
            fields["unit"] = "kg"

    return fields
