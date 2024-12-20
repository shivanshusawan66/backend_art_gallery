import logging
from datetime import timedelta
from typing import Optional
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from ai_mf_backend.utils.v1.authentication.validators import (
    custom_validate_international_phonenumber,
)

from fastapi import APIRouter, Header, Response

from asgiref.sync import sync_to_async

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.models.v1.api.user_authentication import (
    OTPVerificationRequest,
    OTPVerificationResponse,
    ResendOTPRequest,
    ResendOTPResponse,
)
from ai_mf_backend.models.v1.database.user import UserContactInfo, OTPlogs

from ai_mf_backend.utils.v1.authentication.otp import (
    send_otp,
)
from ai_mf_backend.utils.v1.authentication.secrets import (
    jwt_token_checker,
    password_encoder,
)
from ai_mf_backend.utils.v1.authentication.rate_limiting import throttle_otp_requests
from ai_mf_backend.utils.v1.errors import (
    MalformedJWTRequestException,
)

from ai_mf_backend.config.v1.api_config import api_config

logger = logging.getLogger(__name__)

router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.post(
    "/otp_verification", response_model=OTPVerificationResponse, status_code=200
)
async def otp_verification(
    request: OTPVerificationRequest,
    response: Response,  # Use FastAPI Response object
    Authorization: str = Header(),  # Expect token in the Authorization header
) -> OTPVerificationResponse:

    otp_sent = request.otp
    remember_me = request.remember_me

    if not Authorization:
        response.status_code = 422
        return OTPVerificationResponse(
            status=False,
            message="Authorization header is missing.",
            data={},
            status_code=422,
        )
    else:
        try:
            payload = jwt_token_checker(jwt_token=Authorization, encode=False)
        except MalformedJWTRequestException as e:
            response.status_code = 498
            return OTPVerificationResponse(
                status=False,
                message="Invalid JWT token is provided.",
                data={"error": str(e)},
                status_code=498,
            )

    email = payload.get("email")
    mobile_no = payload.get("mobile_number")

    if not any([email, mobile_no]):
        response.status_code = 400  # Set response status code
        return OTPVerificationResponse(
            status=False,
            message="Invalid JWT token is provided, no email or mobile number found.",
            data={},
            status_code=400,
        )

    if all([email, mobile_no]):
        response.status_code = 400  # Set response status code
        return OTPVerificationResponse(
            status=False,
            message="Invalid JWT token is provided, email and mobile number both found.",
            data={},
            status_code=400,
        )

    if email:
        try:
            _ = validate_email(value=email)
        except ValidationError as error_response:
            response.status_code = 422  # Set response status code
            return OTPVerificationResponse(
                status=False,
                message=f"Bad Email provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    elif mobile_no:
        try:
            _ = custom_validate_international_phonenumber(value=mobile_no)
        except ValidationError as error_response:
            response.status_code = 422  # Set response status code
            return OTPVerificationResponse(
                status=False,
                message=f"Bad phone number provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    if not isinstance(otp_sent, int) or not (100000 <= otp_sent <= 999999):
        response.status_code = 422  # Set response status code
        return OTPVerificationResponse(
            status=False,
            message="OTP format is not valid.",
            data={"credentials": payload.get("email") or payload.get("mobile_number")},
            status_code=422,
        )

    if payload["token_type"] == "forgot_password" and not request.password:
        response.status_code = 422  # Set response status code
        return OTPVerificationResponse(
            status=False,
            message="Password is required for password reset.",
            data={"credentials": payload.get("email") or payload.get("mobile_number")},
            status_code=422,
        )

    if request.password:
        try:
            _ = validate_password(password=request.password)
        except ValidationError as error_response:
            response.status_code = 422  # Set response status code
            return OTPVerificationResponse(
                status=False,
                message=f"Bad Password provided: {error_response}",
                data={},
                status_code=422,
            )

    if email:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(email=email).first
        )()
    else:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(mobile_number=mobile_no).first
        )()

    if not user_doc:
        response.status_code = 404  # Set response status code
        return OTPVerificationResponse(
            status=False,
            message="This user does not exist.",
            data={"credentials": payload.get("email") or payload.get("mobile_number")},
            status_code=404,
        )

    user_otp_doc = await sync_to_async(OTPlogs.objects.filter(user=user_doc).first)()

    if not user_otp_doc:
        response.status_code = 404  # Set response status code
        return OTPVerificationResponse(
            status=False,
            message="No OTP found for this user.",
            data={"credentials": payload.get("email") or payload.get("mobile_number")},
            status_code=404,
        )

    if timezone.now().timestamp() >= user_otp_doc.otp_valid.timestamp():
        response.status_code = 403  # Set response status code
        return OTPVerificationResponse(
            status=False,
            message="The OTP provided has expired, please request for a new OTP",
            data={},
            status_code=403,
        )

    if otp_sent != user_otp_doc.otp:
        response.status_code = 403  # Set response status code
        return OTPVerificationResponse(
            status=False,
            message="The OTP that is provided is invalid.",
            data={},
            status_code=403,
        )

    if payload["token_type"] in ["login", "signup"]:
        if payload["token_type"] == "signup":
            user_doc.is_verified = True
            await sync_to_async(user_doc.save)()

        new_payload = {
            "token_type": "login",
            "creation_time": timezone.now().timestamp(),
            "expiry": (
                (
                    timezone.now()
                    + timedelta(hours=api_config.OTP_EXPIRATION_DEFAULT_HOURS)
                ).timestamp()
                if not remember_me
                else (
                    timezone.now()
                    + timedelta(days=api_config.OTP_EXPIRATION_REMEMBER_DAYS)
                ).timestamp()
            ),
        }

        if email:
            new_payload["email"] = email
        else:
            new_payload["mobile_number"] = mobile_no

        new_token = jwt_token_checker(payload=new_payload, encode=True)

        if payload["token_type"] == "signup":
            response.status_code = 201  # Set response status code
            return OTPVerificationResponse(
                status=True,
                message="Signed up successfully",
                data={
                    "credentials": user_doc.email or user_doc.mobile_number,
                    "token": new_token,
                    "user_id": user_doc.user_id,
                    "questionnaire_filled": user_doc.questionnaire_filled,
                },
                status_code=201,
            )
        else:
            response.status_code = 200  # Set response status code
            return OTPVerificationResponse(
                status=True,
                message="Successfully logged in to the Dashboard.",
                data={
                    "credentials": user_doc.email or user_doc.mobile_number,
                    "token": new_token,
                    "user_id": user_doc.user_id,
                    "questionnaire_filled": user_doc.questionnaire_filled,
                },
                status_code=200,
            )

    elif payload["token_type"] == "forgot_password":
        password_added = True if not user_doc.password else False
        user_doc.is_verified = True
        user_doc.password = password_encoder(request.password)
        await sync_to_async(user_doc.save)()
        return OTPVerificationResponse(
            status=True,
            message=(
                "Password is changed successfully."
                if not password_added
                else "Password created successfully."
            ),
            data={
                "credentials": user_doc.email or user_doc.mobile_number,
                "token": None,
            },
        )

    response.status_code = 400  # Set response status code
    return OTPVerificationResponse(
        status=False,
        message="The JWT token provided is invalid for this type of request.",
        data={},
        status_code=400,
    )


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.post("/resend_otp", response_model=ResendOTPResponse, status_code=200)
async def resend_otp(
    request: ResendOTPRequest, response: Response
) -> ResendOTPResponse:

    email = request.email
    mobile_no = request.mobile_no

    if not any([email, mobile_no]):
        response.status_code = 400  # Set response status code
        return ResendOTPResponse(
            status=False,
            message="Either one of email or mobile number is required to proceed with this request.",
            data={"credentials": email if email else mobile_no},
            status_code=400,
        )

    if all([email, mobile_no]):
        response.status_code = 400  # Set response status code
        return ResendOTPResponse(
            status=False,
            message="Both Mobile and email cannot be processed at the same time.",
            data={"credentials": email if email else mobile_no},
            status_code=400,
        )

    if email:
        try:
            _ = validate_email(value=email)
        except ValidationError as error_response:
            response.status_code = 422  # Set response status code
            return ResendOTPResponse(
                status=False,
                message=f"Bad Email provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    elif mobile_no:
        try:
            _ = custom_validate_international_phonenumber(value=mobile_no)
        except ValidationError as error_response:
            response.status_code = 422  # Set response status code
            return ResendOTPResponse(
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
        response.status_code = 404  # Set response status code
        return ResendOTPResponse(
            status=False,
            message="This user does not exist.",
            data={"credentials": request.email or request.mobile_no},
            status_code=404,
        )

    user_id = user_doc.user_id
    can_request, error_message = throttle_otp_requests(user_id)
    if not can_request:
        response.status_code = 429  # Set response status code
        return ResendOTPResponse(
            status=False,
            message=error_message,
            data={"credentials": email or mobile_no},
            status_code=429,
        )

    user_otp_doc = await sync_to_async(OTPlogs.objects.filter(user=user_doc).first)()

    if user_otp_doc:
        time_diff = timezone.now() - user_otp_doc.update_date
        if time_diff <= timedelta(seconds=15):
            response.status_code = 429  # Set response status code
            return ResendOTPResponse(
                status=False,
                message=f"Please wait for {15 - time_diff.seconds} seconds before sending another request.",
                data={"credentials": email if email else mobile_no},
                status_code=429,
            )

    otp = send_otp()
    user_otp_doc.otp = otp
    user_otp_doc.otp_valid = timezone.now() + timedelta(minutes=15)
    await sync_to_async(user_otp_doc.save)()

    response.status_code = 202

    if email:
        message = f"OTP has been sent to {email}. Please check your email."
    else:
        message = f"OTP has been sent to {mobile_no}. Please check your mobile."

    return ResendOTPResponse(
        status=True,
        message=message,
        data={"userdata": {"name": user_doc.email, "otp": otp}},
        status_code=202,
    )
