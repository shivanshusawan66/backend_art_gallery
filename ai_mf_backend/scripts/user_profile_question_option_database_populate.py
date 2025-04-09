import os
import sys
import logging
import django
from datetime import datetime
from django.db import transaction

sys.path.append(rf"{os.getcwd()}")


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)  # Use your project’s settings path

# Set up Django after setting environment variables
django.setup()
logger = logging.getLogger(__name__)

from ai_mf_backend.models.v1.database.user import Gender, MaritalStatus, Occupation
from ai_mf_backend.models.v1.database.financial_details import (
    AnnualIncome,
    MonthlySavingCapacity,
    InvestmentAmountPerYear,
)

# function to populate the Gender,MartialStatus,Occupation,AnnualIncome,MonthlySavingCapacity,InvestmentAmountPerYear


def populate_user_profile_data():
    with transaction.atomic():
        Gender.objects.all().delete()
        MaritalStatus.objects.all().delete()
        Occupation.objects.all().delete()
        AnnualIncome.objects.all().delete()
        MonthlySavingCapacity.objects.all().delete()
        InvestmentAmountPerYear.objects.all().delete()
        logger.info("Existing data cleared successfully.")

    genders = ["Male", "Female", "Other"]
    marital_statuses = ["Single", "Married", "Divorced", "Widowed"]
    occupations = ["Finance", "Engineering", "Entrepreneurship", "Medical"]
    income_categories = [
        "100000-500000",
        "500000-1000000",
        "1000000-1500000",
        "1500000-2000000",
    ]
    saving_categories = ["5000-10000", "10000-20000", "20000-50000", "50000-100000"]
    investment_amount_per_years = [
        "50000-100000",
        "100000-200000",
        "200000-500000",
        "500000-1000000",
    ]

    with transaction.atomic():
        for gender in genders:
            Gender.objects.create(gender=gender)
            print(f"Created Gender:{gender}")

        for status in marital_statuses:
            MaritalStatus.objects.create(marital_status=status)
            print(f"Created Martial Status:{status}")

        for occ in occupations:
            Occupation.objects.create(occupation=occ)
            print(f"Created Occupation: {occ}")

        for income in income_categories:
            AnnualIncome.objects.create(income_category=income)
            print(f"Created Income Category:{income} ")

        for saving in saving_categories:
            MonthlySavingCapacity.objects.create(saving_category=saving)
            print(f"Created Saving Category:{saving} ")

        for investment in investment_amount_per_years:
            InvestmentAmountPerYear.objects.create(
                investment_amount_per_year=investment
            )
            print(f"Created Income Amount Per Year:{investment} ")

    print("User profile page options data populated successfully")


# Execute the function
if __name__ == "__main__":
    populate_user_profile_data()
