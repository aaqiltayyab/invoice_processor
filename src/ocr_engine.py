"""
Requirement 1 : 
Use a free/local OCR library (Tesseract)... 
Save the raw OCR text alongside the source filename.
"""

import os
import pytesseract
from PIL import Image

# Note: Set the Tesseract executable path since it is installed on Windows.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path: str) -> str:
    """
    Extracts text from an image using Tesseract OCR and saves 
    the raw text alongside the source image as a .txt file.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Error: File not found - {image_path}")

    try:
        # Open the image using Pillow
        img = Image.open(image_path)
        
        # Extract text using Tesseract OCR
        raw_text = pytesseract.image_to_string(img)
        
        # Requirement 1: Save the raw OCR text alongside the source filename.
        # Example: 'images/invoice-101.png' -> 'images/invoice-101_raw.txt'
        base_name = os.path.splitext(image_path)[0]
        text_file_path = f"{base_name}_raw.txt"
        
        with open(text_file_path, "w", encoding="utf-8") as file:
            file.write(raw_text)
            
        return raw_text

    except Exception as e:
        print(f"[{image_path}] OCR processing error: {e}")
        return ""