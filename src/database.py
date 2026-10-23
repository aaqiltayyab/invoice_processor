"""
Requirement 4 :
Store valid invoices in SQLite... 
Explain the duplicate key you choose. 
Running the program twice must not insert duplicate invoice records. 
Keep traceability to all source scans, including the duplicate.
"""

import sqlite3
import os

DB_PATH = "invoices.db"

def init_db():
    """
    Database aur tables create karta hai agar wo pehle se nahi hain.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Table for Valid Invoices
    # UNIQUE(vendor, invoice_number) hi hamari Duplicate Key hai.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT,
            invoice_number TEXT,
            invoice_date TEXT,
            currency TEXT,
            subtotal INTEGER,
            tax INTEGER,
            total INTEGER,
            UNIQUE(vendor, invoice_number)
        )
    ''')
    
    # 2. Table for Traceability (Konsi file process hui, kisme error aaya)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            is_valid BOOLEAN,
            needs_review BOOLEAN,
            review_reasons TEXT,
            invoice_id INTEGER,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_invoice_and_file(filename: str, validation_result: dict) -> str:
    """
    Valid invoice ko save karta hai. Agar duplicate ho, toh ignore karke sirf 
    file ki traceability maintain karta hai. Returns a status message.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    is_valid = validation_result['is_valid']
    needs_review = validation_result['needs_review']
    reasons = validation_result['review_reasons']
    data = validation_result['data']
    
    invoice_id = None
    status_msg = "Processed successfully."
    
    # Agar data valid hai, tabhi Invoices table me save karne ki koshish karo
    if is_valid:
        try:
            cursor.execute('''
                INSERT INTO invoices (vendor, invoice_number, invoice_date, currency, subtotal, tax, total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data['vendor'], data['invoice_number'], data['invoice_date'], data['currency'], 
                  data['subtotal'], data['tax'], data['total']))
            invoice_id = cursor.lastrowid
            status_msg = "Valid invoice saved to database."
            
        except sqlite3.IntegrityError:
            # UNIQUE constraint fail hua matlab Duplicate record hai
            cursor.execute('SELECT id FROM invoices WHERE vendor = ? AND invoice_number = ?', 
                           (data['vendor'], data['invoice_number']))
            row = cursor.fetchone()
            if row:
                invoice_id = row[0]
            status_msg = "Duplicate invoice found. Skipping insert, but linking file."
    else:
        status_msg = "Invalid data. Needs review."

    # Traceability: Har file ka record rakho
    try:
        cursor.execute('''
            INSERT INTO processed_files (filename, is_valid, needs_review, review_reasons, invoice_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (os.path.basename(filename), is_valid, needs_review, reasons, invoice_id))
    except sqlite3.IntegrityError:
        status_msg += " (File was already processed earlier)."
        
    conn.commit()
    conn.close()
    
    return status_msg