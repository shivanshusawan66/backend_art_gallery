from typing import Optional
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
import re

def validate_report_type(report_type):
    if not re.match(r"^[A-Za-z\s]+$",report_type):
        raise ValidationError(f"{report_type} is not a valid report type")
    
    if not report_type.strip():
        raise ValidationError("report_type cannot be empty ot only whitespaces.")