from django.core.exceptions import ValidationError

import re
from django.core.exceptions import ValidationError

def validate_alphanumeric_with_spaces(value):
    """
    Validates a text field to ensure data integrity by allowing
    only non-blank, alphanumeric values with optional spaces, 
    without special characters.

    Parameters:
    - value (str): The input to validate.

    Raises:
    - ValidationError: If the value does not meet the validation criteria.
    """
    
    if not value.strip():
        raise ValidationError("This field cannot be blank or whitespace.")

   
    pattern = r"^[A-Za-z0-9\s]+$"

   
    if not re.match(pattern, value):
        raise ValidationError(
            "This field must contain only alphanumeric characters and spaces, without special characters."
        )

    
    return value