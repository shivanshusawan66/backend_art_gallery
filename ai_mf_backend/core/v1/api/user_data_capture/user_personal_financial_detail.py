from PIL import Image, UnidentifiedImageError
import io

from django.utils import timezone
from fastapi import APIRouter, File, HTTPException, Response, Depends, Header, UploadFile, status

from asgiref.sync import sync_to_async

from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

from ai_mf_backend.models.v1.database.user import (
    Occupation,
    UserContactInfo,
    Gender,
    MaritalStatus,
    UserPersonalDetails,
)
from ai_mf_backend.models.v1.database.user_authentication import UserLogs
from ai_mf_backend.models.v1.database.financial_details import (
    AnnualIncome,
    MonthlySavingCapacity,
    InvestmentAmountPerYear,
    UserFinancialDetails,
)
from ai_mf_backend.models.v1.api.user_data import (
    UserPersonalFinancialDetailsUpdateRequest,
    UserPersonalFinancialDetailsUpdateResponse,
    UserPersonalDetailsImageUpdateResponse,
)
from ai_mf_backend.utils.v1.validators.dates import (
    validate_not_future_date,
    validate_reasonable_birth_date,
)
from ai_mf_backend.utils.v1.validators.name import validate_name
from ai_mf_backend.utils.v1.authentication.secrets import jwt_token_checker, login_checker
from ai_mf_backend.utils.v1.validators.profile_update import validate_profile_modification_time

router = APIRouter()


@router.post(
    "/user_personal_financial_details",
    response_model=UserPersonalFinancialDetailsUpdateResponse,
    dependencies=[Depends(login_checker)],
)
async def update_user_personal_financial_details(
    request: UserPersonalFinancialDetailsUpdateRequest,
    response: Response,
    Authorization: str = Header(),
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

        # Validating name
        validate_name(request.name)

        # Validating gender
        gender = await sync_to_async(
            Gender.objects.filter(id=request.gender_id).first
        )()
        if isinstance(request.gender_id, int) and not gender:
            raise ValidationError("Invalid gender provided.")

        # Validating marital status
        marital_status = await sync_to_async(
            MaritalStatus.objects.filter(id=request.marital_status_id).first
        )()
        if isinstance(request.marital_status_id, int) and not marital_status:
            raise ValidationError("Invalid Marital status provided.")

        # Validating occupation
        occupation = await sync_to_async(
            Occupation.objects.filter(id=request.occupation_id).first
        )()
        if isinstance(request.occupation_id, int) and not occupation:
            raise ValidationError("Invalid occupation provided.")

        # Validating annual income
        annual_income = await sync_to_async(
            AnnualIncome.objects.filter(id=request.annual_income_id).first
        )()
        if isinstance(request.annual_income_id, int) and not annual_income:
            raise ValidationError("Invalid Annual income provided.")

        # Validating monthly saving capacity
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

        # Validating investment amount per year
        investment_amount_per_year = await sync_to_async(
            InvestmentAmountPerYear.objects.filter(
                id=request.investment_amount_per_year_id
            ).first
        )()
        if (
            isinstance(request.investment_amount_per_year_id, int)
            and not investment_amount_per_year
        ):
            raise ValidationError("Invalid investment amount per year provided.")

    except ValidationError as e:
        response.status_code = 400
        return UserPersonalFinancialDetailsUpdateResponse(
            status=False,
            message=str(e),
            data={},
            status_code=400,
        )

    user = await sync_to_async(
        UserContactInfo.objects.filter(user_id=request.user_id, deleted=False).first
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
        UserPersonalDetails.objects.filter(user_id=request.user_id, deleted=False).first
    )()
    user_financial = await sync_to_async(
        UserFinancialDetails.objects.filter(
            user_id=request.user_id, deleted=False
        ).first
    )()
    
    if user.user_details_filled:
        try:
            await validate_profile_modification_time(user_personal)
            await validate_profile_modification_time(user_financial)
            response_message = "User personal and financial details updated successfully."
            status_code = status.HTTP_200_OK
        except ValidationError as e:
            response.status_code = 400
            return UserPersonalFinancialDetailsUpdateResponse(
                status=False,
                message=str(e),
                data={},
                status_code=400,
            )
    else:
        response_message = "User personal and financial details created successfully."
        status_code = status.HTTP_201_CREATED
        user.user_details_filled = True
        await sync_to_async(user.save)()

    if not user_personal:
        user_personal = UserPersonalDetails(user=user)
    if not user_financial:
        user_financial = UserFinancialDetails(user=user)

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
    if isinstance(request.regular_source_of_income, bool): 
        user_financial.regular_source_of_income = request.regular_source_of_income
    if isinstance(request.lock_in_period_accepted, bool):
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
        await sync_to_async(user_personal.save)()
        await sync_to_async(user_financial.save)()
        # To update user_logs
        await sync_to_async(UserLogs.objects.create)(
        user=user,
        action="profile_update",
        last_access=timezone.now(),
        ip_details=None,
        device_type=None)

    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "status": False,
                "message": "Validation Error while saving details to the database.",
                "errors": str(e),
            },
        )

    return UserPersonalFinancialDetailsUpdateResponse(
        status=True,
        message=response_message,
        data={"user_id": user.user_id},
        status_code=status_code,
    )


@router.post(
    "/user_personal_details_image_upload",
    response_model=UserPersonalDetailsImageUpdateResponse,
    dependencies=[Depends(login_checker)],
)
async def user_personal_details_image_upload(
    response: Response,
    file: UploadFile = File(...),
    Authorization: str = Header(...),
):
    try:
        decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)
        email = decoded_payload.get("email")
        mobile_number = decoded_payload.get("mobile_number")

        if not any([email, mobile_number]):
            response.status_code = 422
            return UserPersonalDetailsImageUpdateResponse(
                status=False,
                message="Invalid JWT token: no email or mobile number found.",
                data={},
                status_code=422,
            )
        
        if email:
            user = await sync_to_async(UserContactInfo.objects.filter(email=email).first)()
        else:
            user = await sync_to_async(UserContactInfo.objects.filter(mobile_number=mobile_number).first)()

        if not user:
            response.status_code = 400
            return UserPersonalDetailsImageUpdateResponse(
                status=False,
                message="User not found",
                data={},
                status_code=400,
            )
                  
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            image.verify()  
        except (UnidentifiedImageError, Exception) as e:
            response.status_code = 400
            return UserPersonalDetailsImageUpdateResponse(
                status=False,
                message="Uploaded file is not a valid image.",
                data={},
                status_code=400,
            )
        finally:
            await file.close()
    
        content_file = ContentFile(contents, name=file.filename)

        user_details, _ = await sync_to_async(UserPersonalDetails.objects.get_or_create)(user=user)
        user_details.user_image = content_file
        await sync_to_async(user_details.full_clean)()
        await sync_to_async(user_details.save)()

        return UserPersonalDetailsImageUpdateResponse(
            status=True,
            message="Image uploaded successfully",
            data={"image_url": f"{user_details.user_image.name}"},
            status_code=200,
        )

    except ValidationError as ve:
        response.status_code = 400
        return UserPersonalDetailsImageUpdateResponse(
            status=False,
            message=f"Validation error: {ve}",
            data={},
            status_code=400,
        )
    except Exception as e:
        response.status_code = 500
        return UserPersonalDetailsImageUpdateResponse(
            status=False,
            message=f"Internal server error: {str(e)}",
            data={},
            status_code=500,
        )