import logging
from datetime import datetime, timedelta
from django.utils import timezone
from fastapi import APIRouter, Response
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.api.user_authentication import (
    OTPVerificationRequest,
    OTPVerificationResponse,
    ResendOTPRequest,
    ResendOTPResponse,
)
from ai_mf_backend.models.v1.database.user_authentication import UserManagement

from ai_mf_backend.utils.v1.authentication.otp import (
    send_email_otp,
)
from ai_mf_backend.utils.v1.authentication.secrets import (
    jwt_token_checker,
    password_encoder,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/otp_verification", response_model=OTPVerificationResponse, status_code=200
)
async def otp_verification(request: OTPVerificationRequest) -> OTPVerificationResponse:
    """
    Verifies the OTP sent to the user's email or mobile number for password reset, and updates the password
    if the OTP is valid. The JWT token provided in the request must correspond to a 'forgot_password' token type

    Parameters:
    -----------
    request : OTPVerificationRequest
        A Pydantic model that includes the OTP sent to the user, the JWT token, and the new password to set.

    Logic:
    ------
    1. **Token Verification**:
       - The function checks the JWT token using `jwt_token_checker` and decodes the payload.
       - The `token_type` is validated to ensure it is of type `forgot_password`. If not, access is denied.

    2. **Email-based Verification**:
       - If the token contains an email, the function retrieves the user profile from the database based on the email.
       - It checks if the OTP sent by the user matches the OTP stored in the user's profile and if the OTP is still valid (i.e., not expired).
       - If the OTP is valid, the user's password is encoded, updated, and saved to the database.

    3. **Mobile number-based Verification**:
       - If the token contains a mobile number, the function follows a similar process as the email-based flow, but it verifies the user based on their mobile number.
       - It ensures the OTP is valid, updates the password, and saves the changes.

    4. **Error Handling**:
       - If the OTP is expired or incorrect, the function returns a failure response with appropriate error messages.
       - If the user profile is not found (either by email or mobile number), the function returns a 404 error.

    Returns:
    --------
    OTPVerificationResponse: JSON
        A structured response indicating whether the OTP verification was successful or not.
        On success, the user's password is updated, and a success message is returned.
        On failure, error details are provided based on the failure reason (e.g., invalid OTP, expired OTP, user not found).

    Possible Status Codes:
    ----------------------
    - 200: OTP verified successfully, and password updated.
    - 403: Invalid or expired OTP, or invalid token type.
    - 404: User profile not found.

    Example:
    --------
    **Email-based OTP Verification**:
    Request:
        POST /otp_verification
        {
            "otp": "123456",
            "token": "valid_jwt_token",
            "password": "new_password"
        }

    Response:
        {
            "status": true,
            "message": "Password updated successfully.",
            "data": {
                "userdata": {"name": "user@example.com"},
                "otp_verified": true
            }
        }

    **Mobile number-based OTP Verification**:
    Request:
        POST /otp_verification
        {
            "otp": "654321",
            "token": "valid_jwt_token",
            "password": "new_password"
        }

    Response:
        {
            "status": true,
            "message": "Password updated successfully.",
            "data": {
                "userdata": {"name": "+1234567890"},
                "otp_verified": true
            }
        }

    **Failure Response (Invalid OTP)**:
    Response:
        {
            "status": false,
            "message": "Invalid or expired OTP.",
            "data": {
                "error": "OTP verification failed."
            },
            "status_code": 403
        }
    """
    otp_sent = request.otp
    jwt_token = request.token
    payload = jwt_token_checker(jwt_token=jwt_token, encode=False)

    if payload["token_type"] != "forgot_password":
        return OTPVerificationResponse(
            status=False,
            message="Invalid access",
            data={"access_token": "Invalid token."},
            status_code=403,
        )

    if "email" in payload:
        user_doc = await sync_to_async(
            UserManagement.objects.filter(email=payload["email"]).first
        )()
        original_otp = user_doc.otp
        if user_doc:
            if timezone.now().timestamp() <= user_doc.otp_valid_till.timestamp():
                if otp_sent == original_otp:
                    encoded_password = password_encoder(password=request.password)
                    user_doc.password = encoded_password
                    user_doc.updated_at = timezone.now().timestamp()
                    await sync_to_async(user_doc.save)()

                    return OTPVerificationResponse(
                        status=True,
                        message="Password updated successfully.",
                        data={
                            "userdata": {"name": user_doc.email},
                            "otp_verified": True,
                        },
                    )
                else:
                    return OTPVerificationResponse(
                        status=False,
                        message="Invalid or expired OTP.",
                        data={"error": "OTP verification failed."},
                        status_code=403,
                    )
            else:
                return OTPVerificationResponse(
                    status=False,
                    message="expired OTP.",
                    data={"error": "OTP verification failed."},
                    status_code=403,
                )
        else:
            return OTPVerificationResponse(
                status=False,
                message="User not found.",
                data={"error": "User not found."},
                status_code=404,
            )

    elif "mobile_no" in payload:
        user_doc = await sync_to_async(
            UserManagement.objects.filter(mobile_number=payload["mobile_no"]).first
        )()
        original_otp = user_doc.otp
        if user_doc:
            if timezone.now().timestamp() <= user_doc.otp_valid_till.timestamp():
                if otp_sent == original_otp:
                    encoded_password = password_encoder(password=request.password)
                    user_doc.password = encoded_password
                    user_doc.updated_at = timezone.now().timestamp()
                    await sync_to_async(user_doc.save)()

                    return OTPVerificationResponse(
                        status=True,
                        message="Password updated successfully.",
                        data={
                            "userdata": {"name": user_doc.mobile_number},
                            "otp_verified": True,
                        },
                    )
                else:
                    return OTPVerificationResponse(
                        status=False,
                        message="Invalid or expired OTP.",
                        data={"error": "OTP verification failed."},
                        status_code=403,
                    )
            else:
                return OTPVerificationResponse(
                    status=False,
                    message="expired OTP.",
                    data={"error": "OTP verification failed."},
                    status_code=403,
                )
        else:
            return OTPVerificationResponse(
                status=False,
                message="User not found.",
                data={"error": "User not found."},
                status_code=404,
            )


@router.post("/resend_otp", response_model=ResendOTPResponse, status_code=200)
async def resend_otp(request: ResendOTPRequest) -> ResendOTPResponse:
    """
    Resends an OTP (One-Time Password) to the user's email or mobile number for verification purposes.
    The OTP is valid for 15 minutes from the time it is generated. If the user is not found, a 404 error is returned.

    Parameters:
    -----------
    request : ResendOTPRequest
        A Pydantic model that includes either the user's email or mobile number to which the OTP will be resent.

    Logic:
    ------
    1. **Email-based Resending**:
       - If the user provides an email, the function generates a new OTP using `send_email_otp()`.
       - The function looks up the user profile in the `UserManagement` database using the email.
       - If the user is found, the OTP and its expiration time (15 minutes) are saved to the user's profile, and the function returns a success response.
       - If the user is not found, the function returns a 404 error with the message "User not found."

    2. **Mobile number-based Resending**:
       - If the user provides a mobile number, the function follows a similar process as the email-based flow.
       - The OTP is generated, and the user's profile is retrieved using the mobile number.
       - If the user is found, the OTP and its expiration time are updated in the user's profile, and a success message is returned.
       - If the user is not found, a 404 error is returned.

    Returns:
    --------
    ResendOTPResponse: JSON
        A structured response indicating whether the OTP resend request was successful or not.
        On success, a message indicating that the OTP has been sent is returned along with the user's identifier (email or mobile number).
        On failure, an error message is returned.

    Possible Status Codes:
    ----------------------
    - 200: OTP resent successfully.
    - 404: User profile not found.

    Example:
    --------
    **Email-based OTP Resend**:
    Request:
        POST /resend_otp
        {
            "email": "user@example.com"
        }

    Response:
        {
            "status": true,
            "message": "OTP has been sent to user@example.com. Please check.",
            "data": {
                "userdata": {"name": "user@example.com"}
            }
        }

    **Mobile number-based OTP Resend**:
    Request:
        POST /resend_otp
        {
            "mobile_no": "+1234567890"
        }

    Response:
        {
            "status": true,
            "message": "OTP has been sent to +1234567890. Please check.",
            "data": {
                "userdata": {"name": "+1234567890"}
            }
        }

    **Failure Response (User not found)**:
    Response:
        {
            "status": false,
            "message": "User not found.",
            "data": {
                "error": "User not found."
            },
            "status_code": 404
        }
    """
    if request.email:
        otp = send_email_otp()
        user_doc = await sync_to_async(
            UserManagement.objects.filter(email=request.email).first
        )()
        if user_doc:
            user_doc.otp = otp
            user_doc.otp_valid_till = timezone.now() + timedelta(minutes=15)
            user_doc.updated_at = timezone.now()
            await sync_to_async(user_doc.save)()
        else:
            return ResendOTPResponse(
                status=False,
                message="User not found.",
                data={"error": "User not found."},
                status_code=404,
            )
        return ResendOTPResponse(
            status=True,
            message=f"OTP has been sent to {request.email}. Please check.",
            data={"userdata": {"name": user_doc.email, "otp": otp}},
        )
    elif request.mobile_no:
        otp = send_email_otp()
        user_doc = await sync_to_async(
            UserManagement.objects.filter(mobile_number=request.mobile_no).first
        )()
        if user_doc:
            user_doc.otp = otp
            user_doc.otp_valid_till = timezone.now() + timedelta(minutes=15)
            user_doc.updated_at = timezone.now()
            await sync_to_async(user_doc.save)()
        else:
            return ResendOTPResponse(
                status=False,
                message="User not found.",
                data={"error": "User not found."},
                status_code=404,
            )
        return ResendOTPResponse(
            status=True,
            message=f"OTP has been sent to {request.mobile_no}. Please check.",
            data={"userdata": {"name": user_doc.mobile_number, "otp": otp}},
        )
