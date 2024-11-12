from django.core.exceptions import ValidationError

import re
from django.core.exceptions import ValidationError





def validate_number_dash_number(income_category):
    if not re.match(r"^\d+\s*-\s*\d+$", income_category):
        raise ValidationError(f"{income_category} is not a valid  category.")

    if not income_category.strip():
        raise ValidationError(f"Category cannot be empty or only whitespace.")
