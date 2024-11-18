from django.db import models
from django.core.exceptions import ValidationError
import re


def validate_marital_status(marital_status):
    if not re.match(r"^[A-Za-z\s]+$", marital_status):
        raise ValidationError(f"{marital_status} is not a valid marital status.")

    if not marital_status.strip():
        raise ValidationError(f"Marital Status cannot be empty or only whitespace.")


def validate_gender(gender):
    if not re.match(r"^[A-Za-z\s]+$", gender):
        raise ValidationError(f"{gender} is not a valid gender.")

    if not gender.strip():
        raise ValidationError("Gender cannot be empty or only whitespace.")


def validate_occupation(occupation):
    if not re.match(r"^[A-Za-z\s]+$", occupation):
        raise ValidationError(f"{occupation} is not a valid occupation.")

    if not occupation.strip():
        raise ValidationError(f"Occupation cannot be empty or only whitespace.")
