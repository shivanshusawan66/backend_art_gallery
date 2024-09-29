from django.core.exceptions import ValidationError


def validate_mobile_number(value):
    if value and (len(value) != 10 or not value.isdigit()):
        raise ValidationError(
            "Mobile number must be exactly 10 digits long and contain only numbers."
        )
