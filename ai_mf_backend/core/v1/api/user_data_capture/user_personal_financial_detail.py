from fastapi import APIRouter, HTTPException
from django.core.exceptions import ValidationError
from ai_mf_backend.models.v1.database.user import (
    Occupation,
    UserContactInfo,
    Gender,
    MaritalStatus,
    UserPersonalDetails,
)
from ai_mf_backend.models.v1.database.financial_details import (
    AnnualIncome,
    MonthlySavingCapacity,
    InvestmentAmountPerYear,
    UserFinancialDetails,
)
from ai_mf_backend.models.v1.api.user_data import (
    User_Personal_Financial_Details_Update_Request,
    User_Personal_Financial_Details_Update_Response,
)
from asgiref.sync import sync_to_async

router = APIRouter()


@router.post("/user_personal_financial_details/")
async def update_user_personal_financial_details(
    request: User_Personal_Financial_Details_Update_Request,
):
    user = await sync_to_async(
        UserContactInfo.objects.filter(user_id=request.user_id).first
    )()

    if not user:
        return User_Personal_Financial_Details_Update_Response(
            status=False,
            message="User not found",
            data={},
        )

    user_personal = await sync_to_async(
        UserPersonalDetails.objects.filter(user_id=request.user_id).first
    )()
    user_financial = await sync_to_async(
        UserFinancialDetails.objects.filter(user_id=request.user_id).first
    )()

    # Check and fetch optional related models
    gender = None
    marital_status = None
    occupation = None
    annual_income = None
    monthly_saving_capacity = None
    investment_amount_per_year = None

    if request.gender_id:
        gender = await sync_to_async(
            Gender.objects.filter(id=request.gender_id).first
        )()
        if not gender:
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Gender not found",
                data={},
            )

    if request.marital_status_id:
        marital_status = await sync_to_async(
            MaritalStatus.objects.filter(id=request.marital_status_id).first
        )()
        if not marital_status:
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Marital status not found",
                data={},
            )

    if request.occupation_id:
        occupation = await sync_to_async(
            Occupation.objects.filter(id=request.occupation_id).first
        )()
        if not occupation:
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Occupation not found",
                data={},
            )

    if request.annual_income_id:
        annual_income = await sync_to_async(
            AnnualIncome.objects.filter(id=request.annual_income_id).first
        )()
        if not annual_income:
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Annual income not found",
                data={},
            )

    if request.monthly_saving_capacity_id:
        monthly_saving_capacity = await sync_to_async(
            MonthlySavingCapacity.objects.filter(
                id=request.monthly_saving_capacity_id
            ).first
        )()
        if not monthly_saving_capacity:
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Monthly saving capacity not found",
                data={},
            )

    if request.investment_amount_per_year_id:
        investment_amount_per_year = await sync_to_async(
            InvestmentAmountPerYear.objects.filter(
                id=request.investment_amount_per_year_id
            ).first
        )()
        if not investment_amount_per_year:
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Investment amount per year not found",
                data={},
            )

    # Create or update personal and financial details
    if not user_personal:
        user_personal = UserPersonalDetails(
            user=user,
            name=request.name,
            date_of_birth=request.date_of_birth,
            gender=gender,
            marital_status=marital_status,
        )
        await sync_to_async(user_personal.save)()

    if not user_financial:
        user_financial = UserFinancialDetails(
            user=user,
            occupation=occupation,
            annual_income=annual_income,
            monthly_saving_capacity=monthly_saving_capacity,
            investment_amount_per_year=investment_amount_per_year,
            regular_source_of_income=request.regular_source_of_income,
            lock_in_period_accepted=request.lock_in_period_accepted,
            investment_style=request.investment_style,
        )
        try:
            sync_to_async(user_financial.full_clean)()

        except ValidationError as e:

            error_details = e.message_dict  

            raise HTTPException(
                
                status_code=422,

                detail={"status": False, "message": "Validation Error", "errors": error_details},
            )
        await sync_to_async(user_financial.save)()

    # Update existing data if both are present
    if user_personal and user_financial:
        if request.name:
            user_personal.name = request.name

        if request.date_of_birth:
            user_personal.date_of_birth = request.date_of_birth

        if request.gender_id:
            user_personal.gender = gender

        if request.marital_status_id:
            user_personal.marital_status = marital_status

        if request.occupation_id:
            user_financial.occupation = occupation

        if request.annual_income_id:
            user_financial.annual_income = annual_income

        if request.monthly_saving_capacity_id:
            user_financial.monthly_saving_capacity = monthly_saving_capacity

        if request.investment_amount_per_year_id:
            user_financial.investment_amount_per_year = investment_amount_per_year

        if request.regular_source_of_income:
            user_financial.regular_source_of_income = request.regular_source_of_income

        if request.lock_in_period_accepted:
            user_financial.lock_in_period_accepted = request.lock_in_period_accepted

        if request.investment_style:
            user_financial.investment_style = request.investment_style

        await sync_to_async(user_personal.save)()

        try:
            await sync_to_async(user_financial.full_clean)()

        except ValidationError as e:

            error_details = e.message_dict  
            
            raise HTTPException(

                status_code=422,

                detail={"status": False, "message": "Validation Error", "errors": error_details},

            )

        await sync_to_async(user_financial.save)()

    return User_Personal_Financial_Details_Update_Response(
        status=True,
        message="User personal and financial details updated successfully",
        data={"user_id": user.user_id},
    )
