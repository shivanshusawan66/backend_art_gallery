from fastapi import APIRouter, HTTPException, Response
from django.core.exceptions import ValidationError
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
from django.core.exceptions import ValidationError
from ai_mf_backend.utils.v1.validators.dates import (
    validate_not_future_date,
    validate_reasonable_birth_date,
)
from ai_mf_backend.utils.v1.validators.name import validate_name

router = APIRouter()


@router.post("/user_personal_financial_details/")
async def update_user_personal_financial_details(
    request: User_Personal_Financial_Details_Update_Request, response: Response
):
    user = await sync_to_async(
        UserContactInfo.objects.filter(user_id=request.user_id).first
    )()

    if not user:
        response.status_code = 404
        return User_Personal_Financial_Details_Update_Response(
            status=False,
            message="User not found",
            data={},
            status_code=404,
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

    try:
        validate_not_future_date(request.date_of_birth)
        validate_reasonable_birth_date(request.date_of_birth)
    except ValidationError as e:
        response.status_code = 400
        return User_Personal_Financial_Details_Update_Response(
            status=False,
            message=str(e),
            data={},
            status_code=400,
        )

    try:
        validate_name(request.name)
    except ValidationError as e:
        response.status_code = 400
        return User_Personal_Financial_Details_Update_Response(
            status=False,
            message=str(e),
            data={},
            status_code=400,
        )

    if isinstance(request.gender_id, int):
        gender = await sync_to_async(
            Gender.objects.filter(id=request.gender_id).first
        )()
        if not gender:
            response.status_code = 404
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Invalid gender_id provided.",
                data={},
                status_code=404,
            )

    if isinstance(request.marital_status_id, int):
        marital_status = await sync_to_async(
            MaritalStatus.objects.filter(id=request.marital_status_id).first
        )()
        if not marital_status:
            response.status_code = 404
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Invalid marital_status_id provided.",
                data={},
                status_code=404,
            )

    if isinstance(request.occupation_id, int):
        occupation = await sync_to_async(
            Occupation.objects.filter(id=request.occupation_id).first
        )()
        if not occupation:
            response.status_code = 404
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Invalid occupation_id provided.",
                data={},
                status_code=404,
            )

    if isinstance(request.annual_income_id, int):
        annual_income = await sync_to_async(
            AnnualIncome.objects.filter(id=request.annual_income_id).first
        )()
        if not annual_income:
            response.status_code = 404
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Invalid annual_income_id provided.",
                data={},
                status_code=404,
            )

    if isinstance(request.monthly_saving_capacity_id, int):
        monthly_saving_capacity = await sync_to_async(
            MonthlySavingCapacity.objects.filter(
                id=request.monthly_saving_capacity_id
            ).first
        )()
        if not monthly_saving_capacity:
            response.status_code = 404
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Invalid monthly_saving_capacity_id provided.",
                data={},
                status_code=404,
            )

    if isinstance(request.investment_amount_per_year_id, int):
        investment_amount_per_year = await sync_to_async(
            InvestmentAmountPerYear.objects.filter(
                id=request.investment_amount_per_year_id
            ).first
        )()
        if not investment_amount_per_year:
            response.status_code = 404
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message="Invalid investment_amount_per_year_id provided.",
                data={},
                status_code=404,
            )

    # Create or update personal and financial details
    if not user_personal or not user_financial:
        user_personal = UserPersonalDetails(
            user=user,
            name=request.name,
            date_of_birth=request.date_of_birth,
            gender=gender,
            marital_status=marital_status,
        )
        try:
            await sync_to_async(user_personal.full_clean)()  # Run validation

        except ValidationError as e:
            # Capture validation error details
            error_details = e.message_dict  # This contains field-specific errors
            raise HTTPException(
                status_code=422,
                detail={
                    "status": False,
                    "message": "Validation Error",
                    "errors": error_details,
                },
            )
        await sync_to_async(user_personal.save)()
    if not user_financial:
        user_financial = UserFinancialDetails(
            user=user,
            occupation=occupation,
            income_category=annual_income,
            saving_category=monthly_saving_capacity,
            investment_amount_per_year=investment_amount_per_year,
            regular_source_of_income=request.regular_source_of_income,
            lock_in_period_accepted=request.lock_in_period_accepted,
            investment_style=request.investment_style,
        )
        try:
            await sync_to_async(user_financial.full_clean)()
        except ValidationError as e:
            error_details = e.message_dict  # This contains field-specific errors
            raise HTTPException(
                status_code=422,
                detail={
                    "status": False,
                    "message": "Validation Error",
                    "errors": error_details,
                },
            )
        await sync_to_async(user_financial.save)()
        return User_Personal_Financial_Details_Update_Response(
            status=True,
            message="User personal and financial details created successfully.",
            data={"user_id": user.user_id},
            status_code=200,
        )

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
            user_financial.income_category = annual_income

        if request.monthly_saving_capacity_id:
            user_financial.saving_category = monthly_saving_capacity

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
            await sync_to_async(user_personal.full_clean)()  # Run validation
            await sync_to_async(user_financial.full_clean)()
        except ValidationError as e:
            # Capture validation error details
            response.status_code = 422  # Set status code in the response
            return User_Personal_Financial_Details_Update_Response(
                status=False,
                message=f"Validation error",
                data={"errors": e.message_dict},
                status_code=422,
            )
    await sync_to_async(user_personal.save)()
    try:
        await sync_to_async(user_financial.save)()
    except ValidationError as e:
        # Return a structured response with the validation error message
        response.status_code = 422  # Set status code to 422 for validation errors
        return User_Personal_Financial_Details_Update_Response(
            status=False,
            message=str(e),  # Return the validation error message
            data={},
            status_code=422,
        )
    return User_Personal_Financial_Details_Update_Response(
        status=True,
        message="User personal and financial details updated successfully",
        data={"user_id": user.user_id},
    )
