from typing import Optional
from fastapi import APIRouter, HTTPException, Response, Header, Depends
from asgiref.sync import sync_to_async

from ai_mf_backend.models.v1.database.user import (
    UserContactInfo,
    UserPersonalDetails,
)
from ai_mf_backend.models.v1.database.financial_details import UserFinancialDetails
from ai_mf_backend.models.v1.api.user_data import (
    UserPersonalFinancialDetailsResponsesDisplayResponse,
)
from ai_mf_backend.utils.v1.authentication.secrets import login_checker
from django.forms.models import model_to_dict

router = APIRouter()


from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from django.db import DatabaseError


@router.get(
    "/user_personal_financial_details_user_response/{user_id}",
    response_model=UserPersonalFinancialDetailsResponsesDisplayResponse,
    dependencies=[Depends(login_checker)],
)
async def get_user_personal_financial_details(
    user_id: int,
    response: Response,
    Authorization: Optional[str] = Header(None),  # Optional header
):
    try:
        # Fetch user contact info
        user = await sync_to_async(
            UserContactInfo.objects.filter(user_id=user_id).first
        )()

        if not user:
            response.status_code = 404
            return UserPersonalFinancialDetailsResponsesDisplayResponse(
                status=False,
                message="User is not registered with the platform yet.",
                data={},
                status_code=404,
            )

        # Fetch user personal and financial details
        user_personal = await sync_to_async(
            UserPersonalDetails.objects.filter(user=user_id).first
        )()
        user_financial = await sync_to_async(
            UserFinancialDetails.objects.filter(user=user_id).first
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

        # Prepare the data to return
        data = {
            "name": user_personal_data.get("name"),
            "date_of_birth": user_personal_data.get("date_of_birth"),
            "gender": user_personal_data.get("gender"),
            "marital_status": user_personal_data.get("marital_status"),
            "occupation": user_financial_data.get("occupation"),
            "annual_income": user_financial_data.get("income_category"),
            "monthly_saving_capacity": user_financial_data.get("saving_category"),
            "investment_amount_per_year": user_financial_data.get(
                "investment_amount_per_year"
            ),
            "regular_source_of_income": user_financial_data.get(
                "regular_source_of_income"
            ),
            "lock_in_period_accepted": user_financial_data.get(
                "lock_in_period_accepted"
            ),
            "investment_style": user_financial_data.get("investment_style"),
        }

        return UserPersonalFinancialDetailsResponsesDisplayResponse(
            status=True,
            message="Fetched user personal and financial details successfully.",
            data=data,
            status_code=200,
        )

    except DatabaseError as db_err:
        # Handle database errors
        response.status_code = 500
        return UserPersonalFinancialDetailsResponsesDisplayResponse(
            status=False,
            message=f"A database error occurred: {str(db_err)}",
            data={},
            status_code=500,
        )
    except Exception as e:
        # General exception handling for any other issues
        return UserPersonalFinancialDetailsResponsesDisplayResponse(
            status=False,
            message=f"An unexpected error occurred: {str(e)}",
            data={},
            status_code=500,
        )
