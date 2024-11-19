import logging
from datetime import timedelta

from asgiref.sync import sync_to_async

from fastapi import APIRouter, Response

from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from ai_mf_backend.utils.v1.authentication.validators import (
    custom_validate_international_phonenumber,
)
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

from ai_mf_backend.config.v1.api_config import api_config

logger = logging.getLogger(__name__)
router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.post(
    "/password_user_auth",
    status_code=200,
)
async def user_authentication_password(
    request: UserAuthenticationPasswordRequest, response: Response
):
    email = request.email
    mobile_no = request.mobile_no
    password = request.password

    if not any([email, mobile_no]):
        response.status_code = 400  # Set status code in the response
        return UserAuthenticationPasswordResponse(
            status=False,
            message="Either one of email or mobile number is required to proceed with this request.",
            data={"credentials": email if email else mobile_no},
            status_code=400,
        )

    if all([email, mobile_no]):
        response.status_code = 400  # Set status code in the response
        return UserAuthenticationPasswordResponse(
            status=False,
            message="Both Mobile and email cannot be processed at the same time.",
            data={"credentials": email if email else mobile_no},
            status_code=400,
        )

    if email:
        try:
            _ = validate_email(value=email)
        except ValidationError as error_response:
            response.status_code = 422  # Set status code in the response
            return UserAuthenticationPasswordResponse(
                status=False,
                message=f"Bad Email provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    elif mobile_no:
        try:
            _ = custom_validate_international_phonenumber(value=mobile_no)
        except ValidationError as error_response:
            response.status_code = 422  # Set status code in the response
            return UserAuthenticationPasswordResponse(
                status=False,
                message=f"Bad phone number provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    if not password:
        response.status_code = 422  # Set status code in the response
        return UserAuthenticationPasswordResponse(
            status=False,
            message="Password is required to proceed with this request",
            data={"credentials": email if email else mobile_no},
            status_code=422,
        )

    try:
        _ = validate_password(password=password)
    except ValidationError as error_response:
        response.status_code = 422  # Set status code in the response
        return UserAuthenticationPasswordResponse(
            status=False,
            message=f"Bad Password provided: {error_response}",
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


    if user_doc and not user_doc.is_verified:
        password = password_encoder(password=password)
        user_doc.password = password
        await sync_to_async(user_doc.save)()

        user_otp_document = await sync_to_async(
            OTPlogs.objects.filter(user=user_doc.user_id).first
        )()

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
            "expiry": ((timezone.now() + timedelta(minutes=20)).timestamp()),
        }

        if email:
            signup_payload["email"] = email
        else:
            signup_payload["mobile_number"] = mobile_no

        jwt_token = jwt_token_checker(payload=signup_payload, encode=True)

        response.status_code = 202  # Set status code in the response
        return UserAuthenticationPasswordResponse(
            status=True,
            message=f"Otp has been send to {email if email else mobile_no}, please verify it.",
            data={
                "credentials": email if email else mobile_no,
                "token": jwt_token,
                "otp": otp,
            },
            status_code=202,
        )
    elif user_doc and user_doc.password:
        if password_checker(password, user_doc.password):
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

            response.status_code = 200  # Set status code in the response
            return UserAuthenticationPasswordResponse(
                status=True,
                message=f"Successfully logged in to the Dashboard",
                data={
                    "token": jwt_token,
                    "data": {
                        "credentials": email if email else mobile_no,
                        "user_id": user_doc.user_id,
                    },
                },
                status_code=200,
            )
        else:
            response.status_code = 401  # Set status code in the response
            return UserAuthenticationPasswordResponse(
                status=False,
                message=f"Invalid Credentials. Please check your credentials",
                data={"credentials": email if email else mobile_no},
                status_code=401,
            )

    elif user_doc and not user_doc.password:
        response.status_code = 400  # Set status code in the response
        return UserAuthenticationPasswordResponse(
            status=False,
            message=f"User password was not registered, please use Forget Password to reset your password",
            data={"credentials": email if email else mobile_no},
            status_code=400,
        )
    else:
        password = password_encoder(password=password)
        user_doc = UserContactInfo(
            email=email,
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
            "expiry": ((timezone.now() + timedelta(minutes=20)).timestamp()),
        }

        if email:
            signup_payload["email"] = email
        else:
            signup_payload["mobile_number"] = mobile_no

        jwt_token = jwt_token_checker(payload=signup_payload, encode=True)

        response.status_code = 202  # Set status code in the response
        return UserAuthenticationPasswordResponse(
            status=True,
            message=f"Otp has been send to {email if email else mobile_no}, please verify it.",
            data={
                "credentials": email if email else mobile_no,
                "token": jwt_token,
                "otp": otp,
            },
            status_code=202,
        )


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.post(
    "/otp_user_auth",
    status_code=200,
)
async def user_authentication_otp(
    request: UserAuthenticationOTPRequest, response: Response
):
    email = request.email
    mobile_no = request.mobile_no

    if not any([email, mobile_no]):
        response.status_code = 400  # Set status code in the header
        return UserAuthenticationOTPResponse(
            status=False,
            message="Either one of email or mobile number is required to proceed with this request.",
            data={"credentials": email if email else mobile_no},
            status_code=400,
        )

    if all([email, mobile_no]):
        response.status_code = 400  # Set status code in the header
        return UserAuthenticationOTPResponse(
            status=False,
            message="Both Mobile and email cannot be processed at the same time.",
            data={"credentials": email if email else mobile_no},
            status_code=400,
        )

    if email:
        try:
            _ = validate_email(value=email)
        except ValidationError as error_response:
            response.status_code = 422  # Set status code in the header
            return UserAuthenticationOTPResponse(
                status=False,
                message=f"Bad Email provided: {error_response}",
                data={"credentials": email if email else mobile_no},
                status_code=422,
            )

    elif mobile_no:
        try:
            _ = custom_validate_international_phonenumber(value=mobile_no)
        except ValidationError as error_response:
            response.status_code = 422  # Set status code in the header
            return UserAuthenticationOTPResponse(
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

    if user_doc:
        user_id = user_doc.user_id
        can_request, error_message = throttle_otp_requests(user_id)
        if not can_request:
            response.status_code = 429  # Set status code in the header
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
            updated_date = user_otp_document.update_date
            current_time = timezone.now()
            time_diff = current_time - updated_date

            if time_diff <= timedelta(seconds=15):
                response.status_code = 429  # Set status code in the header
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
        
        token_type="login"
        if not user_doc.is_verified:
            token_type = "signup"

        login_payload = {
            "token_type": token_type,
            "creation_time": timezone.now().timestamp(),
            "expiry": (timezone.now() + timedelta(minutes=20)).timestamp(),
        }
        if user_doc.email:
            login_payload["email"] = user_doc.email
        elif user_doc.mobile_number:
            login_payload["mobile_number"] = user_doc.mobile_number
        jwt_token = jwt_token_checker(payload=login_payload, encode=True)

        response.status_code = 202  # Set status code in the header
        return UserAuthenticationOTPResponse(
            status=True,
            message=f"Otp has been send to {email if email else mobile_no}, please verify it. ",
            data={
                "credentials": user_doc.email if email else user_doc.mobile_number,
                "token": jwt_token,
                "otp": otp,
            },
            status_code=202,
        )
    else:
        user_doc = UserContactInfo(
            email=email, mobile_number=mobile_no, is_verified=False
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
            "expiry": (timezone.now() + timedelta(minutes=20)).timestamp(),
        }
        if user_doc.email:
            signup_payload["email"] = user_doc.email
        else:
            signup_payload["mobile_number"] = user_doc.mobile_number
        jwt_token = jwt_token_checker(payload=signup_payload, encode=True)

        response.status_code = 202  # Set status code in the response
        return UserAuthenticationOTPResponse(
            status=True,
            message=f"Otp has been send to {email if email else mobile_no}, please verify it.",
            data={
                "credentials": email if email else mobile_no,
                "token": jwt_token,
                "otp": otp,
            },
            status_code=202,
        )
