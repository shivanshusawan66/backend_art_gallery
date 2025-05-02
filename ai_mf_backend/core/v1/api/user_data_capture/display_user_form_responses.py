from typing import Optional


from fastapi import APIRouter, Response, Depends, Query, Request
from asgiref.sync import sync_to_async

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.utils.v1.authentication.secrets import login_checker
from ai_mf_backend.models.v1.database.user import (
    UserContactInfo,
    UserPersonalDetails,
)

from ai_mf_backend.models.v1.database.financial_details import UserFinancialDetails
from ai_mf_backend.models.v1.api.user_data import UserPersonalFinancialFormData
from ai_mf_backend.models.v1.api.user_data import (
    UserPersonalFinancialDetailsResponsesDisplayResponse,
)
from ai_mf_backend.config.v1.api_config import api_config

router = APIRouter()
from django.core.exceptions import ValidationError


@router.get(
    "/get_user_details_response",
    response_model=UserPersonalFinancialDetailsResponsesDisplayResponse,
    dependencies=[Depends(login_checker)],
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def get_user_personal_financial_details(
    request: Request,
    response: Response,
    user_id: Optional[int] = Query(None, description="User ID"),
):
    try:
        if user_id is None:
            response.status_code = 400
            return UserPersonalFinancialDetailsResponsesDisplayResponse(
                status=False,
                message="user_id is required.",
                data={},
                status_code=400,
            )

        user_exists = await UserContactInfo.objects.filter(
            user_id=user_id, deleted=False
        ).aexists()

        if not user_exists:
            response.status_code = 404
            return UserPersonalFinancialDetailsResponsesDisplayResponse(
                status=False,
                message="User is not registered with the platform yet.",
                data={},
                status_code=404,
            )

        user_personal = await sync_to_async(
            UserPersonalDetails.objects.filter(user=user_id, deleted=False)
            .select_related("gender", "marital_status")
            .first
        )()

        user_financial = await sync_to_async(
            UserFinancialDetails.objects.filter(user=user_id, deleted=False)
            .select_related(
                "occupation",
                "income_category",
                "saving_category",
                "investment_amount_per_year",
            )
            .first
        )()

        if not user_personal and not user_financial:
            response.status_code = 404
            return UserPersonalFinancialDetailsResponsesDisplayResponse(
                status=False,
                message="No personal or financial details found for the user.",
                data={},
                status_code=404,
            )

        # Ensure required fields exist before constructing the Pydantic model
        if (
            not user_personal
            or not user_personal.name
            or not user_personal.date_of_birth
        ):
            response.status_code = 404
            return UserPersonalFinancialDetailsResponsesDisplayResponse(
                status=False,
                message="Required personal details (name or date_of_birth) are missing.",
                data={},
                status_code=404,
            )

        # Build Pydantic model safely
        try:
            data = UserPersonalFinancialFormData(
                name=user_personal.name,
                user_profile_image=(
                    user_personal.user_image.name if user_personal.user_image else None
                ),
                date_of_birth=user_personal.date_of_birth,
                gender=(user_personal.gender.gender if user_personal.gender else None),
                marital_status=(
                    user_personal.marital_status.marital_status
                    if user_personal.marital_status
                    else None
                ),
                occupation=(
                    user_financial.occupation.occupation
                    if user_financial and user_financial.occupation
                    else None
                ),
                annual_income=(
                    user_financial.income_category.income_category
                    if user_financial and user_financial.income_category
                    else None
                ),
                monthly_saving_capacity=(
                    user_financial.saving_category.saving_category
                    if user_financial and user_financial.saving_category
                    else None
                ),
                investment_amount_per_year=(
                    user_financial.investment_amount_per_year.investment_amount_per_year
                    if user_financial and user_financial.investment_amount_per_year
                    else None
                ),
                regular_source_of_income=(
                    user_financial.regular_source_of_income if user_financial else None
                ),
                lock_in_period_accepted=(
                    user_financial.lock_in_period_accepted if user_financial else None
                ),
                investment_style=(
                    user_financial.investment_style if user_financial else None
                ),
            )
        except ValidationError as ve:
            response.status_code = 422
            return UserPersonalFinancialDetailsResponsesDisplayResponse(
                status=False,
                message="Validation error while building response model.",
                data={"errors": ve.errors()},
                status_code=422,
            )

        return UserPersonalFinancialDetailsResponsesDisplayResponse(
            status=True,
            message="Fetched user personal and financial details successfully.",
            data=data.model_dump(),
            status_code=200,
        )

    except Exception as e:
        response.status_code = 500
        return UserPersonalFinancialDetailsResponsesDisplayResponse(
            status=False,
            message=f"An unexpected error occurred: {str(e)}",
            data={},
            status_code=500,
        )
