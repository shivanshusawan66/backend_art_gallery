from typing import Optional
from fastapi import APIRouter, HTTPException, Response, Header, Depends
from asgiref.sync import sync_to_async

from ai_mf_backend.models.v1.database.user import (
    UserContactInfo,
    UserPersonalDetails,
)
from ai_mf_backend.models.v1.database.financial_details import UserFinancialDetails
from ai_mf_backend.models.v1.api.user_data import UserPersonalFinancialDetailsUpdateResponse
from ai_mf_backend.utils.v1.authentication.secrets import login_checker

router = APIRouter()


@router.get(
    "/user_personal_financial_details_user_response/{user_id}",
    response_model=UserPersonalFinancialDetailsUpdateResponse,
    dependencies=[Depends(login_checker)],
)
async def get_user_personal_financial_details(
    user_id: int,
    response: Response,
    Authorization: str = Header(None),  # Optional header
):
    # Fetch user contact info
    print('step0')
    user = await sync_to_async(UserContactInfo.objects.filter(user_id=user_id).first)()
    print(user)
    print('step1')

    if not user:
        response.status_code = 404
        return UserPersonalFinancialDetailsUpdateResponse(
            status=False,
            message="User is not registered with the platform yet.",
            data={},
            status_code=404,
        )

    # Fetch user personal and financial details
    user_personal = await sync_to_async(UserPersonalDetails.objects.filter(user=user_id).first)()
    user_financial = await sync_to_async(UserFinancialDetails.objects.filter(user=user_id).first)()
    print('step2')

    if not user_personal and not user_financial:
        response.status_code = 404
        return UserPersonalFinancialDetailsUpdateResponse(
            status=False,
            message="No personal or financial details found for the user.",
            data={},
            status_code=404,
        )
    
    print(user_personal)
    print(user_financial)
    print('step3')

    
    # data = {
    #     "name": user_personal.name if user_personal else None,
    #     "date_of_birth": user_personal.date_of_birth if user_personal else None,
    #     "gender": await sync_to_async(lambda: user_personal.gender)() if user_personal else None,
    #     "marital_status": await sync_to_async(lambda: user_personal.marital_status)() if user_personal else None,
    #     "occupation": await sync_to_async(lambda: user_financial.occupation)() if user_financial else None,
    #     "annual_income": await sync_to_async(lambda: user_financial.income_category)() if user_financial else None,
    #     "monthly_saving_capacity": await sync_to_async(lambda: user_financial.saving_category)() if user_financial else None,
    #     "investment_amount_per_year": await sync_to_async(lambda: user_financial.investment_amount_per_year)() if user_financial else None,
    #     "regular_source_of_income": await sync_to_async(lambda: user_financial.regular_source_of_income)() if user_financial else None,
    #     "lock_in_period_accepted": await sync_to_async(lambda: user_financial.lock_in_period_accepted)() if user_financial else None,
    #     "investment_style": await sync_to_async(lambda: user_financial.investment_style)() if user_financial else None,
    # }
    print("Finished")

    return UserPersonalFinancialDetailsUpdateResponse(
        status=True,
        message="Fetched user personal and financial details successfully.",
        data={},
        status_code=200,
    )
      