from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_not_future_date(value):
    """
    Validator to ensure a date is not in the future
    """
    if value and value > timezone.now().date():
        raise ValidationError("Future dates are not allowed.")


def validate_reasonable_birth_date(value):
    """
    Validator to ensure birth date is reasonable (e.g., not more than 120 years ago)
    """
    if value:
        min_date = timezone.now().date().replace(year=timezone.now().year - 120)
        if value < min_date:
            raise ValidationError("Birth date is too far in the past.")
