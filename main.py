"""
Requirement 5 :
Produce JSON or CSV containing extracted records, 
validation results, review reasons, and source filenames. 
A failed image must not stop every other file from processing.
"""

import os
import json
import glob
from src.ocr_engine import extract_text_from_image
from src.parser import parse_invoice_text
from src.validator import validate_invoice_data
from src.database import init_db, save_invoice_and_file

# Constants for directory and output file paths
IMAGES_DIR = "images"
REPORT_FILE = "review_report.json"

def process_all_images():
    """
    Processes all images in the specified directory, extracts and validates invoice data,
    stores valid records in the database, and generates a final JSON review report.
    """
    # Initialize database (create tables if they don't exist)
    init_db()
    
    # Fetch all .png files from the images directory
    image_files = glob.glob(os.path.join(IMAGES_DIR, "*.png"))
    
    if not image_files:
        print(f"Error: No images found in the '{IMAGES_DIR}' directory.")
        return

    report_data = []

    print(f"Found {len(image_files)} files. Starting processing...\n")

    for img_path in image_files:
        filename = os.path.basename(img_path)
        print(f"Processing: {filename}...")
        
        # Requirement: A failed image must not stop every other file from processing.
        # Wrapped in a try-except block to ensure fault tolerance.
        try:
            # 1. OCR: Extract raw text from the image
            raw_text = extract_text_from_image(img_path)
            
            # 2. Parse: Extract structured data from the raw text
            parsed_data = parse_invoice_text(raw_text)
            
            # 3. Validate: Check for missing fields and math accuracy (Subtotal + Tax = Total)
            validation_result = validate_invoice_data(parsed_data)
            
            # 4. Database: Save to SQLite (handles duplicate checking and traceability)
            db_status = save_invoice_and_file(img_path, validation_result)
            
            # 5. Compile data for the final report
            report_data.append({
                "source_filename": filename,
                "extracted_record": validation_result["data"],
                "is_valid": validation_result["is_valid"],
                "needs_review": validation_result["needs_review"],
                "review_reasons": validation_result["review_reasons"],
                "db_status": db_status
            })
            
            print(f"  -> Status: {db_status}")
            
        except Exception as e:
            # Gracefully handle unexpected errors to ensure the loop continues
            error_msg = f"Unexpected error: {str(e)}"
            print(f"  -> Failed: {error_msg}")
            report_data.append({
                "source_filename": filename,
                "error": error_msg
            })

    # Requirement 5: Produce JSON containing extracted records, validation results, and review reasons
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)
        
    print(f"\nProcessing complete! Report saved to '{REPORT_FILE}'.")
    print("Database saved to 'invoices.db'.")

if __name__ == "__main__":
    process_all_images()