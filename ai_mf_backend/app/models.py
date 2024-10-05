from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_mobile_number(value):
    if value and (len(value) != 10 or not value.isdigit()):
        raise ValidationError(
            "Mobile number must be exactly 10 digits long and contain only numbers."
        )


class Gender(models.Model):
    gender = models.CharField(max_length=50)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "gender"
    
    def __str__(self):
        return self.gender


class MaritalStatus(models.Model):
    status = models.CharField(max_length=50)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "marital_status"
    
    def __str__(self):
        return self.status


class Occupation(models.Model):
    occupation = models.CharField(max_length=100)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "occupation"
    
    def __str__(self):
        return self.occupation


class AnnualIncome(models.Model):
    income_category = models.CharField(max_length=100)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "annual_income"
    
    def __str__(self):
        return self.income_category


class MonthlySavingCapacity(models.Model):
    saving_category = models.CharField(max_length=100)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "monthly_saving_capacity"
    
    def __str__(self):
        return self.saving_category


class InvestmentAmountPerYear(models.Model):
    investment_amount_per_year = models.CharField(max_length=100)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investment_amount_per_year"
    
    def __str__(self):
        return self.investment_amount_per_year


class UserPersonalDetails(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.ForeignKey(Gender, on_delete=models.PROTECT)
    marital_status = models.ForeignKey(MaritalStatus, on_delete=models.PROTECT)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_personal_details"
    
    def __str__(self):
        return self.name

class UserContactInfo(models.Model):
    user = models.ForeignKey(UserPersonalDetails, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=10, validators=[validate_mobile_number], blank=True, null=True
    )
    password = models.CharField(max_length=100)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_contact_info"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
        ]

    def __str__(self):
        return self.email


class UserOTP(models.Model):
    user = models.ForeignKey(UserPersonalDetails, on_delete=models.CASCADE)
    otp = models.IntegerField()
    otp_valid = models.DateTimeField()
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_otp"
    
    def __str__(self):
        return f"OTP for {self.user.name}"


class UserFinancialDetails(models.Model):
    user = models.ForeignKey(UserPersonalDetails, on_delete=models.CASCADE)
    occupation = models.ForeignKey(Occupation, on_delete=models.PROTECT)
    annual_income = models.ForeignKey(AnnualIncome, on_delete=models.PROTECT)
    monthly_saving_capacity = models.ForeignKey(MonthlySavingCapacity, on_delete=models.PROTECT)
    investment_amount_per_year = models.ForeignKey(InvestmentAmountPerYear, on_delete=models.PROTECT)
    regular_source_of_income = models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False)
    lock_in_period_accepted = models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False)
    investment_style = models.CharField(max_length=10, choices=[('SIP', 'SIP'), ('Lump-Sum', 'Lump-Sum')], default='SIP')
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_financial_details"
    
    def __str__(self):
        return f"Financial Details for {self.user.name}"


class Section(models.Model):
    section_name = models.CharField(max_length=100)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "section"
    
    def __str__(self):
        return self.section_name


class Question(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "question"
    
    def __str__(self):
        return self.question


class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    response = models.CharField(max_length=500)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "response"
    
    def __str__(self):
        return self.response


class UserResponse(models.Model):
    user = models.ForeignKey(UserPersonalDetails, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_response"
    
    def __str__(self):
        return f"Response by {self.user.name} for {self.question.question}"
