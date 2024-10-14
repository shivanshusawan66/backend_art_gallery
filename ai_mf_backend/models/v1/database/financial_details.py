from django.db import models
from ai_mf_backend.models.v1.database.user import UserContactInfo, Occupation

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

class UserFinancialDetails(models.Model):
    user = models.ForeignKey(UserContactInfo, on_delete=models.CASCADE)
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
