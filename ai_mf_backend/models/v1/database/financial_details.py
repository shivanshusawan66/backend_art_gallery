from django.db import models
from ai_mf_backend.models.v1.database.user import UserContactInfo, Occupation
from ai_mf_backend.models.v1.database import SoftDeleteModel
from ai_mf_backend.utils.v1.validators.input import validate_alphanumeric_with_spaces


class AnnualIncome(SoftDeleteModel):
    income_category = models.CharField(max_length=100, unique=True)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "annual_income"
        verbose_name = "Annual Income"
        verbose_name_plural = "Annual Income"

    def __str__(self):
        return self.income_category


class MonthlySavingCapacity(SoftDeleteModel):

    saving_category = models.CharField(
        max_length=100, 
        unique=True, 
        validators=[validate_alphanumeric_with_spaces]
        )
    add_date = models.DateTimeField(
        auto_now_add=True
        )
    update_date = models.DateTimeField(
        auto_now=True
        )

    class Meta:
        db_table = "monthly_saving_capacity"
        verbose_name = "Monthly Saving Capacity"
        verbose_name_plural = "Monthly Saving Capacity"

    def __str__(self):
        return self.saving_category


class InvestmentAmountPerYear(SoftDeleteModel):
    investment_amount_per_year = models.CharField(max_length=100, unique=True)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investment_amount_per_year"
        verbose_name = "Investment Amount Per Year"
        verbose_name_plural = "Investment Amount Per Year"

    def __str__(self):
        return self.investment_amount_per_year


class UserFinancialDetails(SoftDeleteModel):
    user = models.ForeignKey(
        UserContactInfo, on_delete=models.SET_NULL, null=True, blank=True
    )
    occupation = models.ForeignKey(
        Occupation, on_delete=models.SET_NULL, null=True, blank=True
    )
    income_category = models.ForeignKey(
        AnnualIncome, on_delete=models.SET_NULL, null=True, blank=True
    )
    saving_category = models.ForeignKey(
        MonthlySavingCapacity, on_delete=models.SET_NULL, null=True, blank=True
    )
    investment_amount_per_year = models.ForeignKey(
        InvestmentAmountPerYear, on_delete=models.SET_NULL, null=True, blank=True
    )
    regular_source_of_income = models.BooleanField(
        choices=[(True, "Yes"), (False, "No")], default=False, null=True, blank=True
    )
    lock_in_period_accepted = models.BooleanField(
        choices=[(True, "Yes"), (False, "No")], default=False, null=True, blank=True
    )
    investment_style = models.CharField(
        max_length=10,
        choices=[("SIP", "SIP"), ("Lump-Sum", "Lump-Sum")],
        default="SIP",
        null=True,
        blank=True,
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_financial_details"
        verbose_name = "User Financial Detail"
        verbose_name_plural = "User Financial Details"

    def __str__(self):
        return f"Financial Details for {self.user}"
