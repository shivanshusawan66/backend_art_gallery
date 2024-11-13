from django.core.exceptions import ValidationError
import re


def validate_name(value):
    # Regular expression to check if the name contains only letters and spaces
    if not re.match(r"^[a-zA-Z\s]+$", value):
        raise ValidationError("Name should only contain letters and spaces.")
