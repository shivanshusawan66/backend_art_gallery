import re
import logging
import unicodedata
from django.core.exceptions import ValidationError
from fastapi import Request, HTTPException, status
from django.utils.translation import gettext_lazy as _

from phonenumber_field.phonenumber import PhoneNumber, to_python

logger = logging.getLogger(__name__)


def contains_special_chars(input_string):
    # Check if the character is a symbol, punctuation, or other special characters
    for char in input_string:
        if unicodedata.category(char) in [
            "Pc",
            "Pd",
            "Ps",
            "Pe",
            "Pi",
            "Pf",
            "Po",
            "Sm",
            "Sc",
            "Sk",
            "So",
        ]:
            return True
    return False


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "Password must contain at least one uppercase letter.",
                code="password_no_upper",
            )
        if not re.search(r"[0-9]", password):
            raise ValidationError(
                "Password must contain at least one number.",
                code="password_no_number",
            )
        if not contains_special_chars(
            password
        ):  # Use the custom special character check
            raise ValidationError(
                "Password must contain at least one special character (e.g., @, $, !, %, *, ?, or &).",
                code="password_no_special",
            )

    def get_help_text(self):
        return "Your password must contain at least one uppercase letter, one number, and one special character (@, $, !, %, *, ?, or &)."


def custom_validate_international_phonenumber(value):
    # Pre-validation checks
    if not value:
        raise ValidationError("Phone number cannot be empty.")

    if "-" in value:
        raise ValidationError("Phone number cannot contain negative signs.")

    if not value.replace("+", "").isdigit():  # Allow '+' but check for digits
        raise ValidationError(
            "Phone number must contain only digits and an optional leading '+'."
        )

    # Call the existing validation function
    try:
        phone_number = to_python(value)
        logger.info(f"Country code is {phone_number.country_code}")
        if isinstance(phone_number, PhoneNumber) and not phone_number.is_valid():
            raise ValidationError(
                _("The phone number entered is not valid."), code="invalid"
            )

        if not phone_number.country_code:
            raise ValidationError(
                _("This phone number has no country code."), code="invalid"
            )
        if value[1:3] == "91" and value[3] in "012345":
            raise ValidationError(
                "Phone number must start with 6,7, 8, or 9 after the country code."
            )
    except ValidationError as e:
        raise ValidationError(f"Invalid phone number format: {e}")
