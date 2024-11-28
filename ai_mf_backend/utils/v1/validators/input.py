from django.core.exceptions import ValidationError

import re
from django.core.exceptions import ValidationError
from fastapi import HTTPException


def validate_number_dash_number(income_category):
    if not re.match(r"^\d+\s*-\s*\d+$", income_category):
        raise ValidationError(f"{income_category} is not a valid  category.")

    if not income_category.strip():
        raise ValidationError(f"Category cannot be empty or only whitespace.")
    
def validate_fund_id(fund_id: str):
    if not fund_id.isdigit() or fund_id == 0:
        raise HTTPException(
            status_code=400, detail="Fund ID must be a positive integer."
        )
    return int(fund_id)