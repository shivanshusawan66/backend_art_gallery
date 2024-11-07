from phonenumber_field.validators import validate_international_phonenumber
from phonenumber_field.phonenumber import to_python
from django.core.exceptions import ValidationError
def custom_validate_international_phonenumber(value):
    # Pre-validation checks
    if not value:
        raise ValidationError("Phone number cannot be empty.")
    
    if '-' in value:
        raise ValidationError("Phone number cannot contain negative signs.")
    
    if not value.replace("+", "").isdigit():  # Allow '+' but check for digits
        raise ValidationError("Phone number must contain only digits and an optional leading '+'.")
    
    # Call the existing validation function
    try:
        validate_international_phonenumber(value)
    except ValidationError as e:
        raise ValidationError(f"Invalid phone number format: {e}")