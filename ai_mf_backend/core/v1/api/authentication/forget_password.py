import logging
from datetime import timedelta

from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from phonenumber_field.validators import validate_international_phonenumber

from fastapi import Header, APIRouter, Depends

from asgiref.sync import sync_to_async

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.models.v1.api.user_authentication import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from ai_mf_backend.models.v1.database.user import UserContactInfo, OTPlogs
from ai_mf_backend.utils.v1.authentication.otp import send_otp
from ai_mf_backend.utils.v1.authentication.secrets import (
    jwt_token_checker,
    password_encoder,
    login_checker,
    password_checker,
)
from ai_mf_backend.utils.v1.authentication.rate_limiting import throttle_otp_requests

logger = logging.getLogger(__name__)

router = APIRouter()


@limiter.limit("5/minute")
@router.post("/forgot_password", response_model=ForgotPasswordResponse, status_code=200)
async def forgot_password(request: ForgotPasswordRequest):

    email = request.email
    mobile_no = request.mobile_no

    if not any([email, mobile_no]):
        return ForgotPasswordResponse(
            status=False,
            message="Either one of email or mobile number is required to proceed with this request.",
            data={"credentials": email if email else mobile_no},
            status_code=422,
        )

    if all([email, mobile_no]):
        return ForgotPasswordResponse(
            status=False,
            message="Both Mobile and email cannot be processed at the same time.",
            data={"credentials": email if email else mobile_no},
            status_code=422,
        )

    if email:
        try:
            _ = validate_email(value=email)
        except ValidationError as error_response:
            return ForgotPasswordResponse(
                status=False,
                message=f"Bad Email provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    elif mobile_no:
        # We expect the number to be of the format +91 8389273829
        try:
            _ = validate_international_phonenumber(value=mobile_no)
        except ValidationError as error_response:
            return ForgotPasswordResponse(
                status=False,
                message=f"Bad phone number provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    if email:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(email=email).first
        )()
    elif mobile_no:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(mobile_number=mobile_no).first
        )()

    if not user_doc:
        return ForgotPasswordResponse(
            status=False,
            message="This user does not exist.",
            data={"credentials": email or mobile_no},
            status_code=403,
        )

    user_id = user_doc.user_id

    can_request, error_message = throttle_otp_requests(user_id)
    if not can_request:
        return ForgotPasswordResponse(
            status=False,
            message=error_message,
            data={"credentials": email or mobile_no},
            status_code=429,
        )

    if not user_doc.password:
        return ForgotPasswordResponse(
            status=False,
            message="The password for this user does not exist. Please login using OTP",
            data={"credentials": email or mobile_no},
            status_code=403,
        )

    user_otp_document = await sync_to_async(
        OTPlogs.objects.filter(user=user_doc).first
    )()

    if not user_otp_document:
        return ForgotPasswordResponse(
            status=False,
            message="Someone probably tampered with the DB, no previous OTP logs available. Please login using OTP first.",
            data={"credentials": email or mobile_no},
            status_code=403,
        )

    otp = send_otp()
    current_time = timezone.now()

    new_payload = {
        "token_type": "forgot_password",
        "creation_time": timezone.now().timestamp(),
        "expiry": (
            (timezone.now() + timedelta(minutes=15)).timestamp()  # Fixed to 15 minutes
        ),
    }
    if user_doc.email:
        new_payload["email"] = user_doc.email
    elif user_doc.mobile_number:
        new_payload["mobile_number"] = user_doc.mobile_number
    jwt_token = jwt_token_checker(payload=new_payload, encode=True)

    user_otp_document.otp = otp
    user_otp_document.otp_valid = current_time + timedelta(minutes=15)
    await sync_to_async(user_otp_document.save)()

    return ForgotPasswordResponse(
        status=True,
        message=f"OTP has been sent. Please check.",
        data={
            "token": jwt_token,
            "data": {"credentials": email or mobile_no},
            "otp": otp,
        },
    )


@limiter.limit("5/minute")
@router.post(
    "/change_password",
    response_model=ChangePasswordResponse,
    dependencies=[
        Depends(login_checker),
    ],
    status_code=200,
)
async def change_password(
    request: ChangePasswordRequest,
    Authorization: str = Header(...),  # Expect token in the Authorization header
):

    old_password = request.old_password
    new_password = request.new_password

    if not new_password:
        return ChangePasswordResponse(
            status=False,
            message="This request cannot proceed without a new password being provided.",
            data={},
            status_code=403,
        )

    try:
        # Password validators are defined in Django Settings
        _ = validate_password(password=new_password)
    except ValidationError as error_response:
        return ChangePasswordResponse(
            status=False,
            message=f"Bad Password provided: {error_response}",
            data={"credentials": email if email else mobile_no},
            status_code=422,
        )

    jwt_token = Authorization
    decoded_payload = jwt_token_checker(jwt_token=jwt_token, encode=False)

    email = decoded_payload.get("email")
    mobile_no = decoded_payload.get("mobile_no")

    if not any([email, mobile_no]):
        return ChangePasswordResponse(
            status=False,
            message="Invalid JWT token is provided, no email or mobile number found.",
            data={},
            status_code=422,
        )

    if all([email, mobile_no]):
        return ChangePasswordResponse(
            status=False,
            message="Invalid JWT token is provided, email and mobile number both found.",
            data={},
            status_code=422,
        )

    if email:
        try:
            _ = validate_email(value=email)
        except ValidationError as error_response:
            return ChangePasswordResponse(
                status=False,
                message=f"Bad Email provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    elif mobile_no:
        # We expect the number to be of the format +91 8389273829
        try:
            _ = validate_international_phonenumber(value=mobile_no)
        except ValidationError as error_response:
            return ChangePasswordResponse(
                status=False,
                message=f"Bad phone number provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    if email:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(email=email).first
        )()

    elif mobile_no:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(mobile_number=mobile_no).first
        )()

    if not user_doc:
        return ChangePasswordResponse(
            status=False,
            message=f"This User does not exist.",
            data={"credentials": email if email else mobile_no},
            status_code=403,
        )

    if password_checker(old_password, user_doc.password):
        user_doc.password = password_encoder(request.new_password)
        await sync_to_async(user_doc.save)()
        return ChangePasswordResponse(
            status=True,
            message="Your password has been reset successfully!",
            data={},
        )
    else:
        return ChangePasswordResponse(
            status=False,
            message="Old Password didn't match. Please provide the correct Old Password.",
            data={},
            status_code=403,
        )
