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
            data={"userdata": {"name": user_doc.email}},
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
            data={"userdata": {"name": user_doc.mobile_number}},
        )
