from fastapi import APIRouter
from ai_mf_backend.models.v1.database.financial_details import (
    Occupation,
    AnnualIncome,
    MonthlySavingCapacity,
    InvestmentAmountPerYear,
)
from ai_mf_backend.models.v1.database.user import Gender, MaritalStatus
from asgiref.sync import sync_to_async

router = APIRouter()


# Function to fetch options for personal details
@router.get("/options_user_personal_details/")
async def get_personal_options():
    # Fetching gender and marital status options asynchronously
    genders = await sync_to_async(list)(Gender.objects.all())
    marital_statuses = await sync_to_async(list)(MaritalStatus.objects.all())

    # Formatting the fetched data to match the structure you want
    gender_options = [
        { "key": str(gender.id), "label": gender.gender, "value": gender.gender.lower() }
        for gender in genders
    ]
    marital_status_options = [
        {
            "key": str(status.id),
            "label": status.marital_status,
            "value": status.marital_status.lower(),
        }
        for status in marital_statuses
    ]

    # Constructing the response with a structure similar to the "courses" example
    return {
        "genders": {
            "name": "gender",
            "label": "Gender",
            "options": gender_options,
            "type": "dropdown",
            "default": [gender_options[0]["key"]] if gender_options else [],
            "required": False,
        },
        "marital_statuses": {
            "name": "marital_status",
            "label": "Marital Status",
            "options": marital_status_options,
            "type": "dropdown",
            "default": (
                [marital_status_options[0]["key"]] if marital_status_options else []
            ),
            "required": False,
        },
    }


@router.get("/options_user_financial_details/")
async def get_financial_options():
    # Fetching financial options asynchronously
    occupations = await sync_to_async(list)(Occupation.objects.all())
    annual_incomes = await sync_to_async(list)(AnnualIncome.objects.all())
    monthly_saving_capacities = await sync_to_async(list)(
        MonthlySavingCapacity.objects.all()
    )
    investment_amounts_per_year = await sync_to_async(list)(
        InvestmentAmountPerYear.objects.all()
    )

    # Formatting the fetched data
    occupation_options = [
        {
            "key": str(occupation.id),
            "label": occupation.occupation,
            "value": occupation.occupation.lower(),
        }
        for occupation in occupations
    ]
    annual_income_options = [
        {
            "key": str(income.id),
            "label": income.income_category,
            "value": income.income_category.lower(),
        }
        for income in annual_incomes
    ]
    monthly_saving_capacity_options = [
        {
            "key": str(capacity.id),
            "label": capacity.saving_category,
            "value": capacity.saving_category.lower(),
        }
        for capacity in monthly_saving_capacities
    ]
    investment_amount_per_year_options = [
        {
            "key": str(investment.id),
            "label": investment.investment_amount_per_year,
            "value": investment.investment_amount_per_year.lower(),
        }
        for investment in investment_amounts_per_year
    ]

    # Constructing the response with a structure similar to the "courses" example
    return {
        "occupations": {
            "name": "occupation",
            "label": "Occupation",
            "options": occupation_options,
            "type": "dropdown",
            "default": [occupation_options[0]["key"]] if occupation_options else [],
            "required": False,
        },
        "annual_incomes": {
            "name": "annual_income",
            "label": "Annual Income",
            "options": annual_income_options,
            "type": "dropdown",
            "default": (
                [annual_income_options[0]["key"]] if annual_income_options else []
            ),
            "required": False,
        },
        "monthly_saving_capacities": {
            "name": "monthly_saving_capacity",
            "label": "Monthly Saving Capacity",
            "options": monthly_saving_capacity_options,
            "type": "dropdown",
            "default": (
                [monthly_saving_capacity_options[0]["key"]]
                if monthly_saving_capacity_options
                else []
            ),
            "required": False,
        },
        "investment_amounts_per_year": {
            "name": "investment_amount_per_year",
            "label": "Investment Amount Per Year",
            "options": investment_amount_per_year_options,
            "type": "dropdown",
            "default": (
                [investment_amount_per_year_options[0]["key"]]
                if investment_amount_per_year_options
                else []
            ),
            "required": False,
        },
    }
