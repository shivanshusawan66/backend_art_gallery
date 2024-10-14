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
from ai_mf_backend.models.v1.database.user import UserContactInfo,UserOTP

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

    if payload["token_type"] =="logged_in" or payload['token_type']=='signed_up':
        if "email" in payload:
            user_doc = await sync_to_async(
                UserContactInfo.objects.filter(email=payload["email"]).first
            )()
            user_otp=await sync_to_async(
                UserOTP.objects.filter(user=user_doc).first
            )()
        elif "mobile_no" in payload:
            user_doc = await sync_to_async(
                UserContactInfo.objects.filter(mobile_number=payload["mobile_no"]).first
            )()
            user_otp=await sync_to_async(
                UserOTP.objects.filter(user=user_doc).first
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
                                "userdata": {"email_or_mobile_no": user_doc.email if "email" in payload else user_doc.mobile_number },
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
                    message="user not found in otp table",
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
    elif payload["token_type"] =="forgot_password" and request.password:
        if "email" in payload:
            user_doc = await sync_to_async(
                UserContactInfo.objects.filter(email=payload["email"]).first
            )()
            user_otp=await sync_to_async(
                UserOTP.objects.filter(user=user_doc).first
            )()
        elif "mobile_no" in payload:
            user_doc = await sync_to_async(
                UserContactInfo.objects.filter(mobile_number=payload["mobile_no"]).first
            )()
            user_otp=await sync_to_async(
                UserOTP.objects.filter(user=user_doc).first
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
                            message="password changed successfully",
                            data={
                                "userdata": {"email_or_mobile_no": user_doc.email if "email" in payload else user_doc.mobile_number },
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
                    message="user not found in otp table",
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
            UserContactInfo.objects.filter(email=request.email).first
        )()
        if user_doc:
            user_otp = await sync_to_async(
            UserOTP.objects.filter(user=user_doc).first
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
            data={"userdata": {"name": user_doc.email, "otp":otp}},
        )
    elif request.mobile_no:
        otp = send_email_otp()
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(mobile_number=request.mobile_no).first
        )()
        if user_doc:
            user_otp = await sync_to_async(
                UserOTP.objects.filter(user=user_doc.user_id).first
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
            data={"userdata": {"name": user_doc.mobile_number, "otp":otp}},
        )
    else:
        return ResendOTPResponse(
            status=False,
            message="Missing email or mobile number",
            data={"error": "Missing email or mobile number"},
            status_code=400,
        )