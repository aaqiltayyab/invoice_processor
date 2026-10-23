"""
Requirement 6 :
Include at least three focused tests: 
valid-field validation, duplicate/repeated import, and incomplete/ambiguous input. 
Tests can use fixed OCR text so they do not depend on OCR version.
"""

import pytest
from src.parser import parse_invoice_text
from src.validator import validate_invoice_data
from src.database import init_db, save_invoice_and_file
import os

# Test setup: Use a temporary database for testing
os.environ["DB_PATH"] = "test_invoices.db"

# Sample OCR Texts for testing
VALID_OCR_TEXT = """
Vendor: Test Company
Invoice: TST-001
Date: 2026-10-15
Currency: INR
Subtotal: 1000.00
Tax: 180.00
Total: 1180.00
"""

INVALID_OCR_TEXT = """
Vendor: Bad Math Company
Invoice: TST-002
Date: not supplied
Currency: INR
Subtotal: 1000.00
Tax: 180.00
Total: 9999.00
"""

def test_valid_field_validation():
    """Test 1: Valid invoice parsing and validation."""
    parsed_data = parse_invoice_text(VALID_OCR_TEXT)
    validation = validate_invoice_data(parsed_data)
    
    assert validation["is_valid"] is True
    assert validation["needs_review"] is False
    assert validation["data"]["total"] == 118000  # Converted to paise

def test_incomplete_ambiguous_input():
    """Test 2: Invalid invoice (Missing date & Math mismatch)."""
    parsed_data = parse_invoice_text(INVALID_OCR_TEXT)
    validation = validate_invoice_data(parsed_data)
    
    assert validation["is_valid"] is False
    assert validation["needs_review"] is True
    assert "Missing or invalid field: invoice_date" in validation["review_reasons"]
    assert "Math mismatch" in validation["review_reasons"]

def test_duplicate_import():
    """Test 3: Database duplicate prevention."""
    init_db()
    parsed_data = parse_invoice_text(VALID_OCR_TEXT)
    validation = validate_invoice_data(parsed_data)
    
    # First insert should be valid
    status1 = save_invoice_and_file("test_file_1.png", validation)
    assert "Valid invoice saved" in status1
    
    # Second insert with same data should trigger duplicate check
    status2 = save_invoice_and_file("test_file_2.png", validation)
    assert "Duplicate invoice found" in status2