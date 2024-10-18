import logging
from datetime import timedelta

from asgiref.sync import sync_to_async

from fastapi import APIRouter

from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from phonenumber_field.validators import validate_international_phonenumber

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.models.v1.database.user_authentication import UserLogs
from ai_mf_backend.utils.v1.authentication.otp import send_otp
from ai_mf_backend.utils.v1.authentication.secrets import (
    jwt_token_checker,
    password_checker,
    password_encoder,
)
from ai_mf_backend.utils.v1.authentication.rate_limiting import throttle_otp_requests
from ai_mf_backend.models.v1.database.user import (
    UserContactInfo,
    OTPlogs,
)

from ai_mf_backend.models.v1.api.user_authentication import (
    UserAuthenticationPasswordRequest,
    UserAuthenticationPasswordResponse,
    UserAuthenticationOTPRequest,
    UserAuthenticationOTPResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/password_user_auth",
    status_code=200,
)
@limiter.limit("5/minute")
async def user_authentication_password(request: UserAuthenticationPasswordRequest):
    email = request.email
    mobile_no = request.mobile_no
    password = request.password

    if not any([email, mobile_no]):
        return UserAuthenticationPasswordResponse(
            status=False,
            message="Either one of email or mobile number is required to proceed with this request.",
            data={"credentials": email if email else mobile_no},
            status_code=422,
        )

    if all([email, mobile_no]):
        return UserAuthenticationPasswordResponse(
            status=False,
            message="Both Mobile and email cannot be processed at the same time.",
            data={"credentials": email if email else mobile_no},
            status_code=422,
        )

    if not password:
        return UserAuthenticationPasswordResponse(
            status=False,
            message="Password is required to proceed with this request",
            data={"credentials": email if email else mobile_no},
            status_code=422,
        )

    try:
        # Password validators are defined in Django Settings
        _ = validate_password(password=password)
    except ValidationError as error_response:
        return UserAuthenticationPasswordResponse(
            status=False,
            message=f"Bad Password provided: {error_response}",
            data={"credentials": email if email else mobile_no},
            status_code=422,
        )

    if email:
        try:
            _ = validate_email(value=email)
        except ValidationError as error_response:
            return UserAuthenticationPasswordResponse(
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
            return UserAuthenticationPasswordResponse(
                status=False,
                message=f"Bad phone number provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    if email:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(email__iexact=email).first
        )()

    elif mobile_no:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(mobile_number=mobile_no).first
        )()

    if user_doc and user_doc.password:
        if not user_doc.is_verified:
            return UserAuthenticationPasswordResponse(
                status=False,
                message=f"This User is not verified yet.",
                data={"credentials": email if email else mobile_no},
                status_code=403,
            )
        if password_checker(password, user_doc.password):
            # starting login_route
            new_payload = {
                "token_type": "login",
                "creation_time": timezone.now().timestamp(),
                "expiry": (
                    (
                        timezone.now() + timedelta(hours=5)
                    ).timestamp()  # Fixed to 5 hours
                    if not request.remember_me
                    else (timezone.now() + timedelta(days=365)).timestamp()
                ),
            }
            if user_doc.email:
                new_payload["email"] = user_doc.email
            elif user_doc.mobile_number:
                new_payload["mobile_number"] = user_doc.mobile_number
            jwt_token = jwt_token_checker(payload=new_payload, encode=True)

            user_logs = UserLogs(
                user=user_doc,
                ip_details=request.ip_details,
                device_type=request.device_type,
                last_access=timezone.now(),
                action="login",
            )

            await sync_to_async(user_logs.save)()

            return UserAuthenticationPasswordResponse(
                status=True,
                message=f"Successfully logged in to the Dashboard",
                data={
                    "token": jwt_token,
                    "data": {"credentials": email if email else mobile_no},
                },
                status_code=200,
            )
        else:
            return UserAuthenticationPasswordResponse(
                status=False,
                message=f"Invalid Credentials. Please check your credentials",
                data={"credentials": email if email else mobile_no},
                status_code=403,
            )

    elif user_doc and not user_doc.password:
        return UserAuthenticationPasswordResponse(
            status=False,
            message=f"User password was not registered, please try login using OTP.",
            data={"credentials": email if email else mobile_no},
            status_code=403,
        )
    else:
        password = password_encoder(password=password)
        user_doc = UserContactInfo(
            email__iexact=email,
            mobile_number=mobile_no,
            password=password,
            is_verified=False,
        )
        await sync_to_async(user_doc.save)()

        user_otp_document = OTPlogs(
            user=user_doc,
        )

        otp = send_otp()
        user_otp_document.otp = otp
        user_otp_document.otp_valid = timezone.now() + timedelta(minutes=15)

        await sync_to_async(user_otp_document.save)()

        user_logs = UserLogs(
            user=user_doc,
            ip_details=request.ip_details,
            device_type=request.device_type,
            last_access=timezone.now(),
            action="signup",
        )
        await sync_to_async(user_logs.save)()

        signup_payload = {
            "token_type": "signup",
            "creation_time": timezone.now().timestamp(),
            "expiry": (
                (timezone.now() + timedelta(hours=5)).timestamp()  # Fixed to 5 hours
                if not request.remember_me
                else (timezone.now() + timedelta(days=365)).timestamp()
            ),
        }

        if email:
            signup_payload["email"] = email
        else:
            signup_payload["mobile_number"] = mobile_no
        jwt_token = jwt_token_checker(payload=signup_payload, encode=True)
        return UserAuthenticationPasswordResponse(
            status=True,
            message=f"welcome you are the first time time user",
            data={
                "credentials": email if email else mobile_no,
                "token": jwt_token,
            },
            status_code=200,
        )


@router.post(
    "/otp_user_auth",
    status_code=200,
)
@limiter.limit("5/minute")
async def user_authentication_otp(request: UserAuthenticationOTPRequest):
    email = request.email
    mobile_no = request.mobile_no

    if not any([email, mobile_no]):
        return UserAuthenticationOTPResponse(
            status=False,
            message="Either one of email or mobile number is required to proceed with this request.",
            data={"credentials": email if email else mobile_no},
            status_code=422,
        )

    if all([email, mobile_no]):
        return UserAuthenticationOTPResponse(
            status=False,
            message="Both Mobile and email cannot be processed at the same time.",
            data={"credentials": email if email else mobile_no},
            status_code=422,
        )

    if email:
        try:
            _ = validate_email(value=email)
        except ValidationError as error_response:
            return UserAuthenticationOTPResponse(
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
            return UserAuthenticationOTPResponse(
                status=False,
                message=f"Bad phone number provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    if email:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(email__iexact=email).first
        )()
    elif mobile_no:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(mobile_number=mobile_no).first
        )()

    if user_doc:

        user_id = user_doc.user_id
        can_request, error_message = throttle_otp_requests(user_id)
        if not can_request:
            return UserAuthenticationOTPResponse(
                status=False,
                message=error_message,
                data={"credentials": email or mobile_no},
                status_code=429,
            )

        # Login Route
        user_otp_document = await sync_to_async(
            OTPlogs.objects.filter(user=user_doc.user_id).first
        )()
        if not user_otp_document:
            user_otp_document = OTPlogs(
                user=user_doc,
            )
        elif user_otp_document:
            # validation to check and stop user from requesting too many OTPs
            updated_date = user_otp_document.update_date
            # Get the current time
            current_time = timezone.now()

            # Calculate the time difference
            time_diff = current_time - updated_date

            # Check if the update_date is within 15 seconds
            if time_diff <= timedelta(seconds=15):
                return UserAuthenticationOTPResponse(
                    status=False,
                    message=f"Please wait for {time_diff} seconds before sending another request.",
                    data={"credentials": email if email else mobile_no},
                    status_code=429,
                )

        otp = send_otp()

        user_otp_document.otp = otp
        user_otp_document.otp_valid = timezone.now() + timedelta(minutes=15)
        await sync_to_async(user_otp_document.save)()

        login_payload = {
            "token_type": "login",
            "creation_time": timezone.now().timestamp(),
            "expiry": (
                (
                    timezone.now() + timedelta(minutes=15)
                ).timestamp()  # Fixed to 15 minutes
            ),
        }
        if user_doc.email:
            login_payload["email"] = user_doc.email
        elif user_doc.mobile_number:
            login_payload["mobile_number"] = user_doc.mobile_number
        jwt_token = jwt_token_checker(payload=login_payload, encode=True)

        response = UserAuthenticationOTPResponse(
            status=True,
            message=f"OTP successfully send to user ",
            data={
                "data": {
                    "credentials": (
                        user_doc.email if email else user_doc.mobile_number
                    ),
                    "token": jwt_token,
                },
                # TODO: this needs to be removed once we implement sending OTP logic
                "otp": otp,
            },
            status_code=200,
        )
        return response
    else:
        user_doc = UserContactInfo(
            email__iexact=email, mobile_number=mobile_no, is_verified=False
        )
        await sync_to_async(user_doc.save)()

        otp = send_otp()

        user_otp = OTPlogs(
            user=user_doc, otp=otp, otp_valid=timezone.now() + timedelta(minutes=15)
        )
        await sync_to_async(user_otp.save)()

        signup_payload = {
            "token_type": "signup",
            "creation_time": timezone.now().timestamp(),
            "expiry": (
                (
                    timezone.now() + timedelta(minutes=15)
                ).timestamp()  # Fixed to 15 minutes
            ),
        }
        if user_doc.email:
            signup_payload["email"] = user_doc.email
        else:
            signup_payload["mobile_number"] = user_doc.mobile_number
        jwt_token = jwt_token_checker(payload=signup_payload, encode=True)

        response = UserAuthenticationOTPResponse(
            status=True,
            message=f"OTP successfully send to newly created user ",
            data={
                "data": {
                    "credentials": (
                        user_doc.email if email else user_doc.mobile_number
                    ),
                    "token": jwt_token,
                },
                "otp": otp,
            },
            status_code=200,
        )
        return response
