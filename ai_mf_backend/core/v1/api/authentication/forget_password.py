import logging
from datetime import datetime, timedelta
from django.utils import timezone
from fastapi import APIRouter, Response
from asgiref.sync import sync_to_async
from fastapi import Header, Request
from typing import Annotated
from ai_mf_backend.models.v1.api.authentication import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from ai_mf_backend.models.v1.database.user_authentication import UserManagement
from ai_mf_backend.utils.v1.authentication.otp import send_email_otp
from ai_mf_backend.utils.v1.authentication.secrets import (
    jwt_token_checker,
    password_encoder,
    login_checker,
    password_checker,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/forgot_password", response_model=ForgotPasswordResponse, status_code=200)
async def forgot_password(request: ForgotPasswordRequest):
    if request.email:
        user_doc = await sync_to_async(
            UserManagement.objects.filter(email=request.email).first
        )()

        if user_doc:
            otp = send_email_otp()
            current_time = timezone.now()

            payload = {
                "email": request.email,
                "token_type": "forgot_password",
                "creation_time": current_time.timestamp(),
                "expiry": (current_time + timedelta(days=7)).timestamp(),
            }

            jwt_token = jwt_token_checker(payload=payload, encode=True)

            user_doc.otp = otp
            user_doc.otp_valid_till = current_time + timedelta(minutes=15)
            await sync_to_async(user_doc.save)()

            return ForgotPasswordResponse(
                status=True,
                message=f"OTP has been sent to {request.email}. Please check.",
                data={"token": jwt_token, "userdata": {"email": request.email}},
            )
        else:
            return ForgotPasswordResponse(
                status=False,
                message=f"This profile does not exist. {request.email}",
                data={"error": "This profile does not exist."},
                status_code=404,
            )
    elif request.mobile_no:
        user_doc = await sync_to_async(
            UserManagement.objects.filter(mobile_numner=request.mobile_no).first
        )()

        if user_doc:
            otp = send_email_otp()
            current_time = timezone.now()

            payload = {
                "mobile_no": request.mobile_no,
                "token_type": "forgot_password",
                "creation_time": current_time.timestamp(),
                "expiry": (current_time + timedelta(days=7)).timestamp(),
            }

            jwt_token = jwt_token_checker(payload=payload, encode=True)

            user_doc.otp = otp
            user_doc.otp_valid_till = current_time + timedelta(minutes=15)
            await sync_to_async(user_doc.save)()

            return ForgotPasswordResponse(
                status=True,
                message=f"OTP has been sent to {request.mobile_no}. Please check.",
                data={"token": jwt_token, "userdata": {"email": request.mobile_no}},
            )
        else:
            return ForgotPasswordResponse(
                status=False,
                message=f"This profile does not exist. {request.mobile_no}",
                data={"error": "This profile does not exist."},
                status_code=404,
            )


@router.post("/change_password", response_model=ChangePasswordResponse, status_code=200)
async def change_password(request: ChangePasswordRequest):
    jwt_token = await login_checker(request.token)
    decoded_payload = jwt_token_checker(jwt_token=jwt_token, encode=False)
    if "email" in decoded_payload:
        user_doc = await sync_to_async(
            UserManagement.objects.filter(email=decoded_payload["email"]).first
        )()
        if user_doc is None:
            return ChangePasswordResponse(
                status=False,
                message="This profile does not exist.",
                data={"error": "This profile does not exist."},
            )
        if password_checker(request.old_password, user_doc.password):
            user_doc.password = password_encoder(request.password)
            user_doc.updated_at = timezone.now()
            await sync_to_async(user_doc.save)()
            return ChangePasswordResponse(
                status=True,
                message="Your password has been reset successfully!",
                data={},
            )
        else:
            return ChangePasswordResponse(
                status=False,
                message="Password update failed",
                data={
                    "error": "Old Password didn't match. Please provide the correct Old Password."
                },
                status_code=403,
            )
    elif "mobile_no" in decoded_payload:
        user_doc = await sync_to_async(
            UserManagement.objects.filter(
                mobile_number=decoded_payload["mobile_no"]
            ).first
        )()
        print(user_doc)
        if user_doc is None:
            return ChangePasswordResponse(
                status=False,
                message="This profile does not exist.",
                data={"error": "This profile does not exist."},
            )
        if password_checker(request.old_password, user_doc.password):
            user_doc.password = password_encoder(request.password)
            user_doc.updated_at = timezone.now()
            await sync_to_async(user_doc.save)()
            return ChangePasswordResponse(
                status=True,
                message="Your password has been reset successfully!",
                data={},
            )
        else:
            return ChangePasswordResponse(
                status=False,
                message="Password update failed",
                data={"error": "Old Password didn't match. Please provide the correct"},
            )
