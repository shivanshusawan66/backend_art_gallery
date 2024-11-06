import re
from django.core.exceptions import ValidationError

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "Password must contain at least one uppercase letter.",
                code='password_no_upper',
            )
        if not re.search(r"[0-9]", password):
            raise ValidationError(
                "Password must contain at least one number.",
                code='password_no_number',
            )
        if not re.search(r"[@$!%*?&]", password):  # Customize special characters as needed
            raise ValidationError(
                "Password must contain at least one special character (@, $, !, %, *, ?, or &).",
                code='password_no_special',
            )

    def get_help_text(self):
        return (
            "Your password must contain at least one uppercase letter, one number, and one special character (@, $, !, %, *, ?, or &)."
        )
