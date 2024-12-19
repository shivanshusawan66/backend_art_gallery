from django.db import models
import logging
from django.core.exceptions import ValidationError
from ai_mf_backend.models.v1.database.user import UserContactInfo, Occupation
from ai_mf_backend.models.v1.database import SoftDeleteModel
from ai_mf_backend.utils.v1.validators.input import validate_number_dash_number
from ai_mf_backend.utils.v1.validators.profile_update import (
    validate_profile_modification_time,
    track_changes,
)


logger = logging.getLogger(__name__)


class AnnualIncome(SoftDeleteModel):
    income_category = models.CharField(
        max_length=100, unique=True, validators=[validate_number_dash_number]
    )
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
        max_length=100, unique=True, validators=[validate_number_dash_number]
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "monthly_saving_capacity"
        verbose_name = "Monthly Saving Capacity"
        verbose_name_plural = "Monthly Saving Capacity"

    def __str__(self):
        return self.saving_category


class InvestmentAmountPerYear(SoftDeleteModel):
    investment_amount_per_year = models.CharField(
        max_length=100, unique=True, validators=[validate_number_dash_number]
    )
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
        "UserContactInfo", on_delete=models.SET_NULL, null=True, blank=True
    )
    occupation = models.ForeignKey(
        "Occupation", on_delete=models.SET_NULL, null=True, blank=True
    )
    income_category = models.ForeignKey(
        "AnnualIncome", on_delete=models.SET_NULL, null=True, blank=True
    )
    saving_category = models.ForeignKey(
        "MonthlySavingCapacity", on_delete=models.SET_NULL, null=True, blank=True
    )
    investment_amount_per_year = models.ForeignKey(
        "InvestmentAmountPerYear", on_delete=models.SET_NULL, null=True, blank=True
    )
    regular_source_of_income = models.BooleanField(
        choices=[(True, "Yes"), (False, "No")], default=None, null=True, blank=True
    )
    lock_in_period_accepted = models.BooleanField(
        choices=[(True, "Yes"), (False, "No")], default=None, null=True, blank=True
    )
    investment_style = models.CharField(
        max_length=10,
        choices=[("SIP", "SIP"), ("Lump-Sum", "Lump-Sum")],
        default=None,
        null=True,
        blank=True,
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    modification_count = models.PositiveIntegerField(
        default=0
    )  # Track number of modifications

    class Meta:
        db_table = "user_financial_details"
        verbose_name = "User Financial Detail"
        verbose_name_plural = "User Financial Details"

    def __str__(self):
        return f"Financial Details for {self.user}"

    def save(self, *args, **kwargs):
        # Only track changes and validate if this is an update (not creation)
        if self.pk:  # Object exists in the database
            old_instance = UserFinancialDetails.objects.get(pk=self.pk)

            # Track changes in fields
            changed_fields = track_changes(
                old_instance,
                self,
                [
                    "occupation",
                    "income_category",
                    "saving_category",
                    "investment_amount_per_year",
                    "regular_source_of_income",
                    "lock_in_period_accepted",
                    "investment_style",
                ],
            )
            if changed_fields:
                logger.info(
                    f"User {self.user} changed profile fields: {changed_fields}"
                )

            # Validate profile modification restrictions
            try:
                validate_profile_modification_time(self)
            except ValidationError as e:
                raise ValidationError(str(e))

            # Increment modification count if any fields are changed
            self.modification_count += 1
        else:
            # Reset modification count for new users
            self.modification_count = 0

        # Save the instance to the database
        super().save(*args, **kwargs)
