from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date


def validate_not_future_date(value):
    """
    Validator to ensure a date is not in the future.
    """
    # Ensuring 'value' is a date, not a datetime
    if value and value > timezone.now().date():
        raise ValidationError("Future dates are not allowed.")


def validate_reasonable_birth_date(value):
    """
    Validator to ensure birth date is reasonable (e.g., not more than 120 years ago).
    """
    if value:
        # Calculate a minimum date for 120 years ago
        current_year = timezone.now().year
        min_year = current_year - 120
        min_date = date(min_year, value.month, value.day)

        # Validate if date is too far in the past
        if value < min_date:
            raise ValidationError("Birth date is too far in the past.")
