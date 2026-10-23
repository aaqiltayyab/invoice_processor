````markdown
# Invoice Data Processor & Digitization

A Python-based CLI tool to extract, validate, and store invoice data from synthetic images using Tesseract OCR, Regular Expressions, and SQLite.

## Features

- Extracts vendor, invoice number, date, currency, subtotal, tax, and total.
- Avoids floating-point precision errors by storing amounts as integer paise/cents.
- Validates that `Subtotal + Tax = Total` and flags missing fields.
- Uses a unique composite key (`vendor`, `invoice_number`) in SQLite to prevent duplicate records.
- Ensures file processing continues even if a single image fails (fault tolerance).
- Generates a comprehensive `review_report.json` for manual oversight.

## Setup & Installation

**1. Install Tesseract OCR**

- **Windows:** Download via winget (`winget install UB-Mannheim.TesseractOCR`) or installer.
- **Mac:** `brew install tesseract`
- **Linux:** `sudo apt install tesseract-ocr`

**2. Setup Python Environment**

```bash
python -m venv venv
# Windows:
source venv/Scripts/activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```
````

_(Note for Windows users: If Tesseract is not in your PATH, ensure `pytesseract.pytesseract.tesseract_cmd` in `src/ocr_engine.py` points to your correct installation path, e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`)_

## Run & Test Commands

**Process Invoices:**
Place your images in the `images/` folder, then run:

```bash
python main.py

```

_Outputs: `review_report.json` and `invoices.db_`

**Run Tests:**

```bash
pytest

```

## Assumptions & Limitations

- **Assumptions:** Invoices follow a generally consistent vertical format. OCR text is mostly legible. The combination of Vendor name and Invoice Number is globally unique.
- **Limitations:** Extreme skew, low resolution, or handwritten text might cause the Regex patterns to fail. The patterns are currently optimized for standard digital/scanned invoice formats.

## Human Correction & Retries

- **Human Correction:** I would build a simple web dashboard (Django or FastAPI) where the extracted JSON and the original image are displayed side-by-side. Fields marked `needs_review = true` would be highlighted in red for a human operator to correct and submit.
- **Retries:** If Tesseract returns empty or highly garbled text, I would add a retry mechanism using `OpenCV` to preprocess the image (grayscale, thresholding, deskewing) before passing it to the OCR engine again.

---

## Django / DRF Integration Strategy

To expose the saved invoices using Django REST Framework (DRF):

1. **Model:**

```python
class Invoice(models.Model):
    vendor = models.CharField(max_length=255)
    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField()
    currency = models.CharField(max_length=10)
    subtotal = models.IntegerField() # Stored in paise
    tax = models.IntegerField()
    total = models.IntegerField()

    class Meta:
        unique_together = ('vendor', 'invoice_number')

```

2. **Serializer (Validation):** Create an `InvoiceSerializer`. Inside `validate()`, I would add the logic: `if data['subtotal'] + data['tax'] != data['total']: raise serializers.ValidationError("Math mismatch")`.
3. **List Endpoint:** Expose via `ListAPIView` allowing query parameters to filter by `vendor` or `is_reviewed` status.
4. **Access Control:** Enforce security using `permission_classes = [IsAuthenticated]` (using JWT or Session auth) and ensure Row-Level Security if users belong to different tenant organizations.

---

## Past Python/Database Issue Resolved

**Context:** While building a production-grade MCP (Model Context Protocol) Server pipeline for extracting structured JSON from complex unstructured PDFs, I encountered an issue where duplicate entity insertions were crashing the backend.
**The Issue:** The database schema had strict constraints, and the extraction engine occasionally parsed the same document twice (e.g., due to network timeouts retrying the API call).
**My Personal Contribution:** Instead of relying solely on Python-level checks (which fail in concurrent scenarios), I refactored the database schema to use composite `UNIQUE` constraints and implemented `INSERT ... ON CONFLICT DO NOTHING` (or `try/except sqlite3.IntegrityError` in SQLite) in the data ingestion script. This ensured idempotency—running the script 100 times on the same PDF yielded the exact same stable database state without throwing server 500 errors.
