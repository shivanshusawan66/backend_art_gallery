from django.core.exceptions import ValidationError

def validate_investment_type(value):
    if value.lower() not in ('sip','lumpsum'):
        raise ValidationError("Please Enter Valid Investment Type")
    
def validate_fund_name(value):
    if not value:
        raise ValidationError("Fund Name Can't be Null")