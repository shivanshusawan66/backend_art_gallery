import logging
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from phonenumber_field.validators import validate_international_phonenumber

from fastapi import APIRouter, Header

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

logger = logging.getLogger(__name__)

router = APIRouter()


@limiter.limit("5/minute")
@router.post(
    "/otp_verification", response_model=OTPVerificationResponse, status_code=200
)
async def otp_verification(
    request: OTPVerificationRequest,
    Authorization: str = Header(...),  # Expect token in the Authorization header
) -> OTPVerificationResponse:

    jwt_token = Authorization
    otp_sent = request.otp
    remember_me = request.remember_me

    payload = jwt_token_checker(jwt_token=jwt_token, encode=False)

    email = payload.get("email")
    mobile_no = payload.get("mobile_no")

    if not any([email, mobile_no]):
        return OTPVerificationResponse(
            status=False,
            message="Invalid JWT token is provided, no email or mobile number found.",
            data={},
            status_code=400,
        )

    if all([email, mobile_no]):
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
            return OTPVerificationResponse(
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
            return OTPVerificationResponse(
                status=False,
                message=f"Bad phone number provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    if not isinstance(otp_sent, int) or not (100000 <= otp_sent <= 999999):
        return OTPVerificationResponse(
            status=False,
            message="OTP format is not valid.",
            data={"credentials": payload.get("email") or payload.get("mobile_no")},
            status_code=422,
        )

    if payload["token_type"] == "forgot_password" and not request.password:
        return OTPVerificationResponse(
            status=False,
            message="Password is required for password reset.",
            data={"credentials": payload.get("email") or payload.get("mobile_no")},
            status_code=422,
        )

    if request.password:
        # validate the password
        try:
            # Password validators are defined in Django Settings
            _ = validate_password(password=request.password)
        except ValidationError as error_response:
            return OTPVerificationResponse(
                status=False,
                message=f"Bad Password provided: {error_response}",
                data={
                    "credentials": (
                        user_doc.email if "email" in payload else user_doc.mobile_number
                    ),
                },
                status_code=422,
            )

    # Retrieve user based on email or mobile number from the payload
    if "email" in payload:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(email=payload["email"]).first
        )()
    elif "mobile_no" in payload:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(mobile_number=payload["mobile_no"]).first
        )()
    if not user_doc:
        return OTPVerificationResponse(
            status=False,
            message="This user does not exist.",
            data={"credentials": payload.get("email") or payload.get("mobile_no")},
            status_code=404,
        )

    user_otp_doc = await sync_to_async(OTPlogs.objects.filter(user=user_doc).first)()

    if not user_otp_doc:
        return OTPVerificationResponse(
            status=False,
            message="No OTP found for this user.",
            data={"credentials": payload.get("email") or payload.get("mobile_no")},
            status_code=404,
        )

    if timezone.now().timestamp() >= user_otp_doc.otp_valid.timestamp():
        return OTPVerificationResponse(
            status=False,
            message="The OTP provided has expired, please request for a new OTP",
            data={},
            status_code=403,
        )

    if otp_sent != user_otp_doc.otp:
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
                (timezone.now() + timedelta(hours=5)).timestamp()  # Fixed to 5 hours
                if not remember_me
                else (timezone.now() + timedelta(days=365)).timestamp()
            ),
        }

        if "email" in payload:
            new_payload["email"] = payload["email"]
        elif "mobile_no" in payload:
            new_payload["mobile_no"] = payload["mobile_no"]

        new_token = jwt_token_checker(payload=new_payload, encode=True)

        return OTPVerificationResponse(
            status=True,
            message="The user is verified successfully",
            data={
                "credentials": (
                    user_doc.email if "email" in payload else user_doc.mobile_number
                ),
                "token": new_token,
            },
        )
    elif payload["token_type"] == "forgot_password":

        password_encoded = password_encoder(request.password)
        user_doc.password = password_encoded
        await sync_to_async(user_doc.save)()
        return OTPVerificationResponse(
            status=True,
            message="Password is changed successfully.",
            data={
                "credentials": (
                    user_doc.email if "email" in payload else user_doc.mobile_number
                ),
                "token": None,
            },
        )
    else:
        return OTPVerificationResponse(
            status=False,
            message="The JWT token provided is invalid for this type of request.",
            data={},
            status_code=400,
        )


@limiter.limit("5/minute")
@router.post("/resend_otp", response_model=ResendOTPResponse, status_code=200)
async def resend_otp(request: ResendOTPRequest) -> ResendOTPResponse:

    email = request.email
    mobile_no = request.mobile_no

    if not any([email, mobile_no]):
        return ResendOTPResponse(
            status=False,
            message="Either one of email or mobile number is required to proceed with this request.",
            data={"credentials": email if email else mobile_no},
            status_code=400,
        )

    if all([email, mobile_no]):
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
            return ResendOTPResponse(
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
        return OTPVerificationResponse(
            status=False,
            message="This user does not exist.",
            data={"credentials": request.email or request.mobile_no},
            status_code=404,
        )

    user_id = user_doc.user_id
    can_request, error_message = throttle_otp_requests(user_id)
    if not can_request:
        return ResendOTPResponse(
            status=False,
            message=error_message,
            data={"credentials": email or mobile_no},
            status_code=429,
        )

    
    user_otp_doc = await sync_to_async(OTPlogs.objects.filter(user=user_doc).first)()

    if not user_otp_doc:
            user_otp_doc = OTPlogs(
                user=user_doc,
            )
    elif user_otp_doc:
        # validation to check and stop user from requesting too many OTPs
        updated_date = user_otp_doc.update_date
        # Get the current time
        current_time = timezone.now()

        # Calculate the time difference
        time_diff = current_time - updated_date

        # Check if the update_date is within 15 seconds
        if time_diff <= timedelta(seconds=15):
            return ResendOTPResponse(
                status=False,
                message=f"Please wait for {time_diff} seconds before sending another request.",
                data={"credentials": email if email else mobile_no},
                status_code=429,
            )

    otp = send_otp()
    user_otp_doc.otp = otp
    user_otp_doc.otp_valid = timezone.now() + timedelta(minutes=15)
    await sync_to_async(user_otp_doc.save)()

    return ResendOTPResponse(
        status=True,
        message=f"OTP has been sent to {request.email}. Please check.",
        data={"userdata": {"name": user_doc.email, "otp": otp}},
    )
