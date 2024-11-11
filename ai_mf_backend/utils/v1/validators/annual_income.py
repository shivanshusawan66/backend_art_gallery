import re
from django.db import models
from django.core.exceptions import ValidationError


def validate_annual_income(income_category):
    if not re.match(r"^\d+\s*-\s*\d+$", income_category):
        raise ValidationError(f"{income_category} is not a valid income category.")

    if not income_category.strip():
        raise ValidationError(f"Income category cannot be empty or only whitespace.")
