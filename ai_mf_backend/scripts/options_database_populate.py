import os
import sys
import logging
import django
from django.db import connection, transaction

sys.path.append(rf"{os.getcwd()}")


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)  


django.setup()
logger = logging.getLogger(__name__)


from ai_mf_backend.models.v1.database.user import Gender, MaritalStatus, Occupation
from ai_mf_backend.models.v1.database.financial_details import (
    AnnualIncome,
    MonthlySavingCapacity,
    InvestmentAmountPerYear,
)
from ai_mf_backend.models.v1.database.mf_category_wise import (
    MutualFundType,
    MutualFundSubcategory
)
from ai_mf_backend.models.v1.database.mf_filter_parameters import (
    MFFilterColors,
    MFFilterParameters
)

def reset_pk_sequence(model):
    """Reset the primary key sequence for the given model (PostgreSQL only)."""
    table_name = model._meta.db_table
    sequence_sql = f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1"
    with connection.cursor() as cursor:
        cursor.execute(sequence_sql)

def populate_user_profile_data():
    with transaction.atomic():
        Gender.objects.all().delete()
        MaritalStatus.objects.all().delete()
        Occupation.objects.all().delete()
        AnnualIncome.objects.all().delete()
        MonthlySavingCapacity.objects.all().delete()
        InvestmentAmountPerYear.objects.all().delete()
        MutualFundSubcategory.objects.all().delete()
        MutualFundType.objects.all().delete()
        MFFilterParameters.objects.all().delete()
        MFFilterColors.objects.all().delete()
        logger.info("Existing data cleared successfully.")

        # Reset primary keys
        reset_pk_sequence(Gender)
        reset_pk_sequence(MaritalStatus)
        reset_pk_sequence(Occupation)
        reset_pk_sequence(AnnualIncome)
        reset_pk_sequence(MonthlySavingCapacity)
        reset_pk_sequence(InvestmentAmountPerYear)
        reset_pk_sequence(MutualFundSubcategory)
        reset_pk_sequence(MutualFundType)
        reset_pk_sequence(MFFilterParameters)
        reset_pk_sequence(MFFilterColors)
        logger.info("Primary key sequences reset.")

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
    mutual_fund_type = [
        "Commodity",
        "Debt",
        "Equity",
        "Hybrid",
        "Other",
    ]

    mutual_fund_subcategories  = {
    "Commodity":[
      "FoFs",
      "FoFs (Domestic)",
      "ETFs"
    ],
    "Debt":[
      "Long Duration",
      "Liquid",
      "Debt -Interval Funds",
      "Credit Risk Fund",
      "Short Duration",
      "Medium to Long Duration",
      "Sector Funds",
      "Medium Duration",
      "ETFs",
      "Overnight Fund",
      "Money Market",
      "Low Duration",
      "Corporate Bond",
      "Dynamic Bond",
      "Ultra Short Duration",
      "Banking and PSU Fund",
      "Fixed Maturity Plans",
      "Floating Rate",
      "Gilt"
    ],
    "Equity":  [
      "Mid Cap Fund",
      "Index Funds",
      "Focused Fund",
      "Contra",
      "Dividend Yield",
      "Large Cap Fund",
      "Thematic Fund",
      "Sector Funds",
      "Value Fund",
      "ETFs",
      "Equity Linked Savings Scheme",
      "Flexi Cap Fund",
      "Small cap Fund",
      "Large & Mid Cap",
      "Multi Cap Fund"
    ],
    "Hybrid":  [
      "Dynamic Asset Allocation",
      "Multi Asset Allocation",
      "Aggressive Hybrid Fund",
      "Balanced Advantage",
      "Real Estate",
      "Capital Protection Funds",
      "Arbitrage Fund",
      "Equity Savings",
      "Conservative Hybrid Fund",
      "Balanced Hybrid Fund"
    ],
    "Other":  [
      "Solution Oriented - Retirement Fund",
      "FoFs (Domestic)",
      "FoFs (Overseas)",
      "ETFs - Other",
      "Solution Oriented - Children's Fund"
    ],
    }

    mf_parameters = [
    "jalpha_y",
    "beta_y",
    "_1yrret",
    "treynor_y",
    "sd_y",
    "sharpe_y",
    "_5yearret",
    "_3yearret",
    ]

    mf_colors = [
        "Blue", "Brown", "High", "Low", "Low to Moderate", "Moderate", "Moderately High", "Very High",
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
        for category in mutual_fund_type:
            MutualFundType.objects.create(fund_type=category)
            print(f"Created Mutual Fund Category:{category} ")
            
        for fund_type_name, subcategories in mutual_fund_subcategories.items():
            try:
                fund_type = MutualFundType.objects.get(fund_type=fund_type_name)
            except MutualFundType.DoesNotExist:
                print(f"Fund type '{fund_type_name}' not found. Skipping its subcategories.")
                continue

            for subcategory in subcategories:
                MutualFundSubcategory.objects.create(
                    fund_subcategory=subcategory,
                    fund_type_id=fund_type
                )
                print(f"Created Mutual Fund Subcategory:{subcategory} under {fund_type_name}")
        
        for mf_parameter in mf_parameters:
            MFFilterParameters.objects.create(parameter_name=mf_parameter)
            print(f"Created Mutual Fund Parameter:{mf_parameter}")
        
        for mf_color in mf_colors:
            MFFilterColors.objects.create(color_name=mf_color)
            print(f"Created Mutual Fund Color:{mf_color}")

    print("Option Population script completed successfully.")


# Execute the function
if __name__ == "__main__":
    populate_user_profile_data()
