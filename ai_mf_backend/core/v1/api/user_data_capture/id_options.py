from fastapi import APIRouter
from ai_mf_backend.models.v1.database.financial_details import  Occupation, AnnualIncome, MonthlySavingCapacity, InvestmentAmountPerYear
from ai_mf_backend.models.v1.database.user import Gender, MaritalStatus
from asgiref.sync import sync_to_async

router = APIRouter()

# Function to fetch options for personal details
@router.get("/options_user_personal_details/")
async def get_personal_options():
    # Fetching gender and marital status options asynchronously
    genders = await sync_to_async(list)(Gender.objects.all())
    marital_statuses = await sync_to_async(list)(MaritalStatus.objects.all())

    # Formatting the fetched data
    gender_options = [{"id": gender.id, "label": gender.gender} for gender in genders]
    marital_status_options = [{"id": status.id, "label": status.status} for status in marital_statuses]

    return {
        "genders": gender_options,
        "marital_statuses": marital_status_options
    }

# Function to fetch options for financial details
@router.get("/options_user_financial_details/")
async def get_financial_options():
    # Fetching financial options asynchronously
    occupations = await sync_to_async(list)(Occupation.objects.all())
    annual_incomes = await sync_to_async(list)(AnnualIncome.objects.all())
    monthly_saving_capacities = await sync_to_async(list)(MonthlySavingCapacity.objects.all())
    investment_amounts_per_year = await sync_to_async(list)(InvestmentAmountPerYear.objects.all())

    # Formatting the fetched data
    occupation_options = [{"id": occupation.id, "label": occupation.occupation} for occupation in occupations]
    annual_income_options = [{"id": income.id, "label": income.income_category} for income in annual_incomes]
    monthly_saving_capacity_options = [{"id": capacity.id, "label": capacity.saving_category} for capacity in monthly_saving_capacities]
    investment_amount_per_year_options = [{"id": investment.id, "label": investment.investment_amount_per_year} for investment in investment_amounts_per_year]

    return {
        "occupations": occupation_options,
        "annual_incomes": annual_income_options,
        "monthly_saving_capacities": monthly_saving_capacity_options,
        "investment_amounts_per_year": investment_amount_per_year_options,
    }