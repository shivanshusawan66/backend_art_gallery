import logging
from datetime import datetime, timedelta
from django.utils import timezone
from fastapi import APIRouter, Response
from asgiref.sync import sync_to_async
from app.schemas.v1.authentication import(OTPVerificationRequest,OTPVerificationResponse,ResendOTPRequest,ResendOTPResponse)
from app.models import UserManagement

from utils.v1.authentication.otp import (
    send_email_otp,
    send_email_otp_verification_done,
)
from utils.v1.authentication.secrets import (
    jwt_token_checker,
    password_encoder,
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/otp_verification", response_model=OTPVerificationResponse, status_code=200)
async def otp_verification(request: OTPVerificationRequest) -> OTPVerificationResponse:
    """
    After signup or forgot password, the user will have to verify their credentials using an OTP received in their mail.
    This function expects OTP, JWT token, email from payload.
    Steps:
    -> OTP, email and JWT token are loaded from the post request
    -> Payload is extracted out of the JWT token
    -> If token_type is not signup or forgot_password status 403 is returned to enhance security
    -> user is looked for using the email
    -> is user doc is found
        -> OTP sent is extracted from the database
        -> if the user is verified status 409 is returned
        -> if the user is not verified
            -> If the OTP match and are not expired, 
               - If token_type is forgot_password the password is encoded
               - else password is set to None
               - new payload is generated and status 200 is returned
            -> else, status 403 is returned
    -> if user doc is not found status 422 is returned
    :return: Response
    """

    otp_sent = request.otp
    jwt_token = request.token
    payload = jwt_token_checker(jwt_token=jwt_token, encode=False)

    if payload['token_type'] not in ["signup", "forgot_password"]:
        return OTPVerificationResponse(
            status=False,
            message="Invalid access",
            data={"access_token": "Invalid token."},
            status_code=403
        )

    user_doc = await sync_to_async(UserManagement.objects.filter(email=payload['email']).first)()

    if user_doc is None:
        return OTPVerificationResponse(
            status=False,
            message="User not found.",
            data={"error": "This user does not exist."},
            status_code=422
        )

    original_otp = user_doc.otp

    if user_doc and payload["token_type"] == "signup" and user_doc.is_verified:
        return OTPVerificationResponse(
            status=False,
            message="User creation failed",
            data={"email": "This user already exists."},
            status_code=409
        )

    elif user_doc and payload["token_type"] == "signup" and not user_doc.is_verified:
        # logger.info(f"Date -> {datetime.utcnow()} db datetime -> {user_doc.otp_valid_till}")
        if otp_sent == original_otp and (timezone.now().timestamp() <= user_doc. otp_valid_till.timestamp()):
            unique_id = str(user_doc.id)
            name = user_doc.name
            email = user_doc.email
            current_time = timezone.now()

            payload = {
                "name": name,
                "email": email,
                "unique_id": unique_id,
                "token_type": "logged_in",
                "creation_time": current_time.timestamp(),
                "expiry": (current_time + timedelta(days=7)).timestamp(),
            }

            jwt_token = jwt_token_checker(payload=payload, encode=True)

            user_doc.is_verified = True
            user_doc.last_accessed = current_time
            user_doc.updated_at = current_time

            await sync_to_async(user_doc.save)() 

            send_email_otp_verification_done(receiver_email_id=email)

            return OTPVerificationResponse(
                status=True,
                message="Your email has been verified.",
                data={
                    "token": jwt_token,
                    "userdata": {"name": user_doc.name},
                    "otp_verified": True,
                },
            )
        else:
            return OTPVerificationResponse(
                status=False,
                message="Invalid or expired OTP.",
                data={"error": "OTP verification failed."},
                status_code=403
            )
    elif payload["token_type"] == "forgot_password":
        # logger.info(f"Date -> {datetime.utcnow()} db datetime -> {user_doc.otp_valid_till}")
        if otp_sent == original_otp and (timezone.now().timestamp() <= user_doc.otp_valid_till.timestamp()):
            encoded_password = password_encoder(password=request.password)
            user_doc.password = encoded_password
            user_doc.updated_at = timezone.now().timestamp()
            await sync_to_async(user_doc.save)()

            return OTPVerificationResponse(
                status=True,
                message="Password updated successfully.",
                data={
                    "userdata": {"name": user_doc.name},
                    "otp_verified": True,
                },
            )
        else:
            return OTPVerificationResponse(
                status=False,
                message="Invalid or expired OTP.",
                data={"error": "OTP verification failed."},
                status_code=403
            )
    else:
        return OTPVerificationResponse(
            status=False,
            message="OTP verification failed.",
            data={"error": "No data found."},
            status_code=422
        )


@router.post("/resend_otp", response_model=ResendOTPResponse, status_code=200)
async def resend_otp(request: ResendOTPRequest) -> ResendOTPResponse:
    """
    Resends the OTP in case the user has not received it or if the OTP has expired.
    This function expects a JWT token and email from the payload.

    Steps:
    1. The JWT token is extracted from the request and decoded.
    2. If the token type is not "signup" or "forgot_password", an invalid access response is returned.
    3. The email is extracted from the decoded payload.
    4. The function checks if the user exists in the database using the provided email.
    5. If the user exists:
       - If the token type is "forgot_password", a new OTP is generated and sent regardless of the user's verification status.
       - If the token type is "signup" and the user is already verified, a conflict response is returned.
       - If the token type is "signup" and the user is not verified, a new OTP is generated and sent.
    6. If the user does not exist, a failed response is returned.

    :param request: ResendOTPRequest object containing the JWT token.
    :return: ResendOTPResponse object with the status, message, and data (if applicable).
    """
    jwt_token = request.token

    try:
        payload = jwt_token_checker(jwt_token=jwt_token, encode=False)
    except Exception as e:
        return ResendOTPResponse(
            status=False,
            message="Invalid token.",
            data={"error": str(e)},
            status_code=403
        )

    if payload["token_type"] not in ["signup", "forgot_password"]:
        return ResendOTPResponse(
            status=False,
            message="Invalid access",
            data={"access_token": "Invalid token."},
            status_code=403
        )

    email = payload["email"]

    # Check if the user exists
    user_doc = await sync_to_async(UserManagement.objects.filter(email=payload['email']).first)()

    if user_doc:
        
        # If the token type is "forgot_password", allow OTP resend regardless of verification status
        if payload["token_type"] == "forgot_password":
            otp = send_email_otp(receiver_email_id=email)

            user_doc.otp = otp
            user_doc.otp_valid_till = timezone.now() + timedelta(minutes=15)
            user_doc.updated_at =timezone.now()
            await sync_to_async(user_doc.save)() 

            return ResendOTPResponse(
                status=True,
                message=f"OTP has been sent to {email}. Please check.",
                data={"token": jwt_token, "userdata": {"name": payload.get("name")}},
            )
        
        if user_doc.is_verified:
            return ResendOTPResponse(
                status=False,
                message="User already verified.",
                data={"email": "This user is already verified."},
                status_code=409
            )

        # If the user exists but is not verified (for signup)
        otp = send_email_otp(receiver_email_id=email)

        user_doc.otp = otp
        user_doc.otp_valid_till = timezone.now() + timedelta(minutes=15)
        user_doc.updated_at = timezone.now()
        await sync_to_async(user_doc.save)() 

        return ResendOTPResponse(
            status=True,
            message=f"OTP has been sent to {email}. Please check.",
            data={"token": jwt_token, "userdata": {"name": payload.get("name")}},
        )

    else:
        return ResendOTPResponse(
            status=False,
            message="Resend OTP failed",
            data={"user_data": "No data found"},
            status_code=422
        )