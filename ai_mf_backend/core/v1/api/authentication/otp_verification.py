import logging
from datetime import timedelta
from django.utils import timezone
from fastapi import APIRouter, Header
from asgiref.sync import sync_to_async
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

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/otp_verification", response_model=OTPVerificationResponse, status_code=200
)
async def otp_verification(
    request: OTPVerificationRequest,
    Authorization: str = Header(...),  # Expect token in the Authorization header
) -> OTPVerificationResponse:

    jwt_token = Authorization
    otp_sent = request.otp

    payload = jwt_token_checker(jwt_token=jwt_token, encode=False)

    if not isinstance(otp_sent, int) or len(str(otp_sent)) != 6:
        return OTPVerificationResponse(
            status=False,
            message="OTP format is not valid.",
            data={"credentials": payload.get("email") or payload.get("mobile_no")},
            status_code=422,
        )

    if payload["token_type"] == "forgot_password":
        if not request.password:
            return OTPVerificationResponse(
                status=False,
                message="Password is required for password reset.",
                data={"credentials": payload.get("email") or payload.get("mobile_no")},
                status_code=422,
            )

    elif payload["token_type"] in ["login", "signup"]:
        # Retrieve user based on email or mobile number from the payload
        if "email" in payload:
            user_doc = await sync_to_async(
                UserContactInfo.objects.filter(email=payload["email"]).first
            )()
            user_otp = await sync_to_async(
                OTPlogs.objects.filter(user=user_doc).first
            )()
        elif "mobile_no" in payload:
            user_doc = await sync_to_async(
                UserContactInfo.objects.filter(mobile_number=payload["mobile_no"]).first
            )()
            user_otp = await sync_to_async(
                OTPlogs.objects.filter(user=user_doc).first
            )()
        else:
            return OTPVerificationResponse(
                status=False,
                message="Invalid email or mobile number",
                data={"error": "User data not found."},
                status_code=403,
            )

        if user_doc:
            if user_otp:
                if timezone.now().timestamp() <= user_otp.otp_valid.timestamp():
                    if otp_sent == user_otp.otp:
                        return OTPVerificationResponse(
                            status=True,
                            message="Welcome to the Dashboard",
                            data={
                                "userdata": {
                                    "email_or_mobile_no": (
                                        user_doc.email
                                        if "email" in payload
                                        else user_doc.mobile_number
                                    )
                                },
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
                        message="Expired OTP.",
                        data={"error": "OTP verification failed."},
                        status_code=403,
                    )
            else:
                return OTPVerificationResponse(
                    status=False,
                    message="User not found in OTP table.",
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
    elif payload["token_type"] == "forgot_password" and request.password:
        # The password reset logic remains the same
        if "email" in payload:
            user_doc = await sync_to_async(
                UserContactInfo.objects.filter(email=payload["email"]).first
            )()
            user_otp = await sync_to_async(
                OTPlogs.objects.filter(user=user_doc).first
            )()
        elif "mobile_no" in payload:
            user_doc = await sync_to_async(
                UserContactInfo.objects.filter(mobile_number=payload["mobile_no"]).first
            )()
            user_otp = await sync_to_async(
                OTPlogs.objects.filter(user=user_doc).first
            )()
        else:
            return OTPVerificationResponse(
                status=False,
                message="Invalid email or mobile number",
                data={"error": "User data not found."},
                status_code=403,
            )

        if user_doc:
            if user_otp:
                if timezone.now().timestamp() <= user_otp.otp_valid.timestamp():
                    if otp_sent == user_otp.otp:
                        password_encoded = password_encoder(request.password)
                        user_doc.password = password_encoded
                        await sync_to_async(user_doc.save)()
                        return OTPVerificationResponse(
                            status=True,
                            message="Password changed successfully",
                            data={
                                "userdata": {
                                    "email_or_mobile_no": (
                                        user_doc.email
                                        if "email" in payload
                                        else user_doc.mobile_number
                                    )
                                },
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
                        message="Expired OTP.",
                        data={"error": "OTP verification failed."},
                        status_code=403,
                    )
            else:
                return OTPVerificationResponse(
                    status=False,
                    message="User not found in OTP table.",
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
    else:
        return OTPVerificationResponse(
            status=False,
            message="Invalid request.",
            data={"error": "Invalid request."},
            status_code=400,
        )


@router.post("/resend_otp", response_model=ResendOTPResponse, status_code=200)
async def resend_otp(request: ResendOTPRequest) -> ResendOTPResponse:
    if request.email:
        otp = send_otp()
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(email=request.email).first
        )()
        if user_doc:
            user_otp = await sync_to_async(
                OTPlogs.objects.filter(user=user_doc).first
            )()

            if user_otp:
                user_otp.otp = otp
                user_otp.otp_valid = timezone.now() + timedelta(minutes=15)
                await sync_to_async(user_otp.save)()
            else:
                return ResendOTPResponse(
                    status=False,
                    message="User not found in otp table",
                    data={"error": "User not found in otp table"},
                    status_code=404,
                )
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
        otp = send_otp()
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(mobile_number=request.mobile_no).first
        )()
        if user_doc:
            user_otp = await sync_to_async(
                OTPlogs.objects.filter(user=user_doc.user_id).first
            )()
            if user_otp:
                user_otp.otp = otp
                user_otp.otp_valid = timezone.now() + timedelta(minutes=15)
                await sync_to_async(user_otp.save)()
            else:
                return ResendOTPResponse(
                    status=False,
                    message="User not found in otp table",
                    data={"error": "User not found in otp table"},
                    status_code=404,
                )
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
    else:
        return ResendOTPResponse(
            status=False,
            message="Missing email or mobile number",
            data={"error": "Missing email or mobile number"},
            status_code=400,
        )
