"""
Step 3 :
Validate required fields and subtotal + tax = total. 
Missing or ambiguous values must enter a needs_review output with a reason; 
do not silently guess or discard them.
"""

def validate_invoice_data(parsed_data: dict) -> dict:
    """
    Validates the extracted invoice data.
    Checks for missing mandatory fields and verifies if Subtotal + Tax = Total.
    Returns a dictionary with validation status and review reasons.
    """
    needs_review = False
    review_reasons = []

    # 1. Check for missing required fields
    required_fields = ["vendor", "invoice_number", "invoice_date", "total"]
    for field in required_fields:
        if not parsed_data.get(field):
            needs_review = True
            review_reasons.append(f"Missing or invalid field: {field}")

    # 2. Math validation: Subtotal + Tax == Total
    # Treating missing subtotal or tax as 0 for calculation purposes
    subtotal = parsed_data.get("subtotal") or 0
    tax = parsed_data.get("tax") or 0
    total = parsed_data.get("total")

    if total is not None:
        if (subtotal + tax) != total:
            needs_review = True
            review_reasons.append(f"Math mismatch: Subtotal ({subtotal}) + Tax ({tax}) != Total ({total})")

    # 3. Return the final structured result
    return {
        "is_valid": not needs_review,
        "needs_review": needs_review,
        "review_reasons": "; ".join(review_reasons) if review_reasons else None,
        "data": parsed_data
    }