"""
Step 2 : 
Extract invoice number, vendor, invoice date, currency, subtotal, tax, and total. 
Normalize dates and amounts. 
Store amounts as integer paise rather than binary floating-point money.
"""

import re
from datetime import datetime

def normalize_amount(amount_str: str) -> int:
    """
    Converts an amount string (e.g., '1,234.56') to integer paise/cents (123456).
    """
    if not amount_str:
        return None
    
    clean_str = re.sub(r'[^\d\.]', '', amount_str)
    try:
        return int(round(float(clean_str) * 100))
    except ValueError:
        return None

def normalize_date(date_str: str) -> str:
    """
    Attempts to normalize a date string to 'YYYY-MM-DD' format.
    """
    if not date_str or "not supplied" in date_str.lower():
        return None
        
    date_str = date_str.strip()
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y", "%d %b %Y"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
            
    return date_str

def parse_invoice_text(raw_text: str) -> dict:
    """
    Extracts invoice fields from raw OCR text using specific Regular Expressions.
    """
    # Updated Patterns based on the exact image formats
    vendor_match = re.search(r"Vendor\s*[:\-]?\s*(.+)", raw_text, re.IGNORECASE)
    invoice_no_match = re.search(r"Invoice\s*[:\-]?\s*([A-Z0-9\-]+)", raw_text, re.IGNORECASE)
    date_match = re.search(r"Date\s*[:\-]?\s*([0-9]{1,4}[-/ \.][A-Za-z0-9]+[-/ \.][0-9]{1,4})", raw_text, re.IGNORECASE)
    currency_match = re.search(r"Currency\s*[:\-]?\s*([A-Za-z]+)", raw_text, re.IGNORECASE)
    
    # \b ensures it only matches "Total", not "Subtotal"
    subtotal_match = re.search(r"\bSubtotal\s*[:\-]?\s*([\d,\.]+)", raw_text, re.IGNORECASE)
    tax_match = re.search(r"\bTax\s*[:\-]?\s*([\d,\.]+)", raw_text, re.IGNORECASE)
    total_match = re.search(r"\bTotal\s*[:\-]?\s*([\d,\.]+)", raw_text, re.IGNORECASE)

    parsed_data = {
        "vendor": vendor_match.group(1).strip() if vendor_match else None,
        "invoice_number": invoice_no_match.group(1).strip() if invoice_no_match else None,
        "invoice_date": normalize_date(date_match.group(1)) if date_match else None,
        "currency": currency_match.group(1).strip() if currency_match else None, 
        "subtotal": normalize_amount(subtotal_match.group(1)) if subtotal_match else None,
        "tax": normalize_amount(tax_match.group(1)) if tax_match else None,
        "total": normalize_amount(total_match.group(1)) if total_match else None
    }
    
    return parsed_data