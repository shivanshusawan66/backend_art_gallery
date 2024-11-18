from fastapi import APIRouter, HTTPException, Response

from asgiref.sync import sync_to_async

from django.core.exceptions import ValidationError
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
    UserPersonalFinancialDetailsUpdateRequest,
    UserPersonalFinancialDetailsUpdateResponse,
)

from ai_mf_backend.utils.v1.validators.dates import (
    validate_not_future_date,
    validate_reasonable_birth_date,
)
from ai_mf_backend.utils.v1.validators.name import validate_name

router = APIRouter()


@router.post("/user_personal_financial_details/")
async def update_user_personal_financial_details(
    request: UserPersonalFinancialDetailsUpdateRequest, response: Response
):
    gender = None
    marital_status = None
    occupation = None
    annual_income = None
    monthly_saving_capacity = None
    investment_amount_per_year = None
    try:
        # Validating date of birth
        validate_not_future_date(request.date_of_birth)
        validate_reasonable_birth_date(request.date_of_birth)

        # validating name
        validate_name(request.name)

        # validating gender
        gender = await sync_to_async(
            Gender.objects.filter(id=request.gender_id).first
        )()
        if isinstance(request.gender_id, int) and not gender:
            raise ValidationError("Invalid gender provided.")

        # validating marital status
        marital_status = await sync_to_async(
            MaritalStatus.objects.filter(id=request.marital_status_id).first
        )()
        if isinstance(request.marital_status_id, int) and not marital_status:
            raise ValidationError("Invalid Marital status provided.")

        # validating occupation
        occupation = await sync_to_async(
            Occupation.objects.filter(id=request.occupation_id).first
        )()
        if isinstance(request.occupation_id, int) and not occupation:
            raise ValidationError("Invalid occupation provided.")

        # validating annual income
        annual_income = await sync_to_async(
            AnnualIncome.objects.filter(id=request.annual_income_id).first
        )()
        if isinstance(request.annual_income_id, int) and not annual_income:
            raise ValidationError("Invalid Annual income provided.")

        # validating monthly saving capacity
        monthly_saving_capacity = await sync_to_async(
            MonthlySavingCapacity.objects.filter(
                id=request.monthly_saving_capacity_id
            ).first
        )()
        if (
            isinstance(request.monthly_saving_capacity_id, int)
            and not monthly_saving_capacity
        ):
            raise ValidationError("Invalid Monthly saving capacity provided.")

        # validating investment ammount per year
        investment_amount_per_year = await sync_to_async(
            InvestmentAmountPerYear.objects.filter(
                id=request.investment_amount_per_year_id
            ).first
        )()
        if (
            isinstance(request.investment_amount_per_year_id, int)
            and not investment_amount_per_year
        ):
            raise ValidationError("Invalid investment ammount per year provided.")

    except ValidationError as e:
        status_code = 400
        response.status_code = status_code
        return UserPersonalFinancialDetailsUpdateResponse(
            status=False,
            message=str(e),
            data={},
            status_code=status_code,
        )

    user = await sync_to_async(
        UserContactInfo.objects.filter(user_id=request.user_id).first
    )()

    if not user:
        response.status_code = 404
        return UserPersonalFinancialDetailsUpdateResponse(
            status=False,
            message="User is not registered with the platform yet, please check your login details.",
            data={},
            status_code=404,
        )

    user_personal = await sync_to_async(
        UserPersonalDetails.objects.filter(user_id=request.user_id).first
    )()
    user_financial = await sync_to_async(
        UserFinancialDetails.objects.filter(user_id=request.user_id).first
    )()

    response_message = "User personal and financial details updated successfully."
    status_code = 200

    # Create or update personal and financial details
    if not user_personal:
        user_personal = UserPersonalDetails()
        response_message = "User personal and financial details created successfully."
        status_code = 201

    if request.name:
        user_personal.name = request.name
    if request.date_of_birth:
        user_personal.date_of_birth = request.date_of_birth
    if request.gender_id:
        user_personal.gender = gender
    if request.marital_status_id:
        user_personal.marital_status = marital_status

    if not user_financial:
        user_financial = UserFinancialDetails()
        response_message = "User personal and financial details created successfully."
        status_code = 201

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

    try:
        await sync_to_async(
            user_personal.full_clean
        )()  # Run validation for user personal details
        await sync_to_async(
            user_financial.full_clean
        )()  # Run validation for user financial details

    except ValidationError as e:
        # Capture validation error details
        error_details = e.message_dict  # This contains field-specific errors
        raise HTTPException(
            status_code=422,
            detail={
                "status": False,
                "message": "Validation Error while saving details to the database.",
                "errors": error_details,
            },
        )

    await sync_to_async(user_personal.save)()
    await sync_to_async(user_financial.save)()

    response.status_code = status_code
    return UserPersonalFinancialDetailsUpdateResponse(
        status=True,
        message=response_message,
        data={"user_id": user.user_id},
        status_code=status_code,
    )
