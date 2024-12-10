from typing import Optional


from fastapi import APIRouter, Response, Depends, Query, Request
from asgiref.sync import sync_to_async
from django.forms.models import model_to_dict

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.utils.v1.authentication.secrets import login_checker
from ai_mf_backend.models.v1.database.user import (
    UserContactInfo,
    UserPersonalDetails,
    Gender,
    MaritalStatus,
    Occupation,
)
from ai_mf_backend.models.v1.database.financial_details import (
    AnnualIncome,
    MonthlySavingCapacity,
    InvestmentAmountPerYear,
)
from ai_mf_backend.models.v1.database.financial_details import UserFinancialDetails
from ai_mf_backend.models.v1.api.user_data import UserPersonalFinancialFormData
from ai_mf_backend.models.v1.api.user_data import (
    UserPersonalFinancialDetailsResponsesDisplayResponse,
)
from ai_mf_backend.config.v1.api_config import api_config

router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/get_user_details_response",
    response_model=UserPersonalFinancialDetailsResponsesDisplayResponse,
    dependencies=[Depends(login_checker)],
)
async def get_user_personal_financial_details(
    request: Request,
    response: Response,
    user_id: Optional[int] = Query(None, description="User ID"),
):
    try:
        # Fetch user contact info
        if not user_id:
            response.status_code = 404
            return UserPersonalFinancialDetailsResponsesDisplayResponse(
                status=False,
                message="User_id is not provided,please provide it",
                data={},
                status_code=404,
            )

        user_check = await UserContactInfo.objects.filter(
            user_id=user_id, deleted=False
        ).aexists()

        if not user_check:
            response.status_code = 404
            return UserPersonalFinancialDetailsResponsesDisplayResponse(
                status=False,
                message="User is not registered with the platform yet.",
                data={},
                status_code=404,
            )

        # Fetch user personal and financial details
        user_personal = await sync_to_async(
            UserPersonalDetails.objects.filter(user=user_id, deleted=False).first
        )()
        user_financial = await sync_to_async(
            UserFinancialDetails.objects.filter(user=user_id, deleted=False).first
        )()

        if not user_personal and not user_financial:
            response.status_code = 404
            return UserPersonalFinancialDetailsResponsesDisplayResponse(
                status=False,
                message="No personal or financial details found for the user.",
                data={},
                status_code=404,
            )

        # If the models are not None, convert them to dictionaries
        user_personal_data = model_to_dict(user_personal) if user_personal else {}
        user_financial_data = model_to_dict(user_financial) if user_financial else {}

        gender_id = user_personal_data.get("gender")
        gender_instance = await sync_to_async(
            Gender.objects.filter(id=gender_id).only("gender").first
        )()

        marital_status_id = user_personal_data.get("marital_status")
        marital_status_instance = await sync_to_async(
            MaritalStatus.objects.filter(id=marital_status_id)
            .only("marital_status")
            .first
        )()

        occupation_id = user_financial_data.get("occupation")

        occupation_instance = await sync_to_async(
            Occupation.objects.filter(id=occupation_id).only("occupation").first
        )()

        annual_income_id = user_financial_data.get("income_category")
        print(annual_income_id)
        annual_income_instance = await sync_to_async(
            AnnualIncome.objects.filter(id=annual_income_id)
            .only("income_category")
            .first
        )()

        saving_category_id = user_financial_data.get("saving_category")
        saving_category_instance = await sync_to_async(
            MonthlySavingCapacity.objects.filter(id=saving_category_id)
            .only("saving_category")
            .first
        )()

        investment_amount_per_year_id = user_financial_data.get(
            "investment_amount_per_year"
        )
        investment_amount_per_year_instance = await sync_to_async(
            InvestmentAmountPerYear.objects.filter(id=investment_amount_per_year_id)
            .only("investment_amount_per_year")
            .first
        )()
        # Prepare the data to return
        data = UserPersonalFinancialFormData(
            name=user_personal_data.get("name"),
            date_of_birth=user_personal_data.get("date_of_birth"),
            gender=gender_instance.gender,
            marital_status=marital_status_instance.marital_status,
            occupation=occupation_instance.occupation,
            annual_income=annual_income_instance.income_category,
            monthly_saving_capacity=saving_category_instance.saving_category,
            investment_amount_per_year=investment_amount_per_year_instance.investment_amount_per_year,
            regular_source_of_income=user_financial_data.get(
                "regular_source_of_income"
            ),
            lock_in_period_accepted=user_financial_data.get("lock_in_period_accepted"),
            investment_style=user_financial_data.get("investment_style"),
        )

        return UserPersonalFinancialDetailsResponsesDisplayResponse(
            status=True,
            message="Fetched user personal and financial details successfully.",
            data=data.model_dump(),
            status_code=200,
        )
    except Exception as e:
        # General exception handling for any other issues
        return UserPersonalFinancialDetailsResponsesDisplayResponse(
            status=False,
            message=f"An unexpected error occurred: {str(e)}",
            data={},
            status_code=500,
        )
