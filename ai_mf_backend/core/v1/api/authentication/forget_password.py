import logging
from datetime import datetime, timedelta
from django.utils import timezone
from fastapi import APIRouter,Response
from asgiref.sync import sync_to_async
from fastapi import Header,Request
from typing import Annotated
from app.schemas.v1.authentication import(ForgotPasswordRequest,ForgotPasswordResponse,ChangePasswordRequest,ChangePasswordResponse)
from app.models import UserManagement
from utils.v1.authentication.otp import send_email_otp
from utils.v1.authentication.secrets import (
    jwt_token_checker,
    password_encoder,
    login_checker,password_checker
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/forgot_password", response_model=ForgotPasswordResponse, status_code=200)
async def forgot_password(request: ForgotPasswordRequest):
    email = request.email
    user_doc = await sync_to_async(UserManagement.objects.filter(email=request.email).first)()

    if user_doc:
        otp = send_email_otp(receiver_email_id=email)
        current_time = timezone.now()

        payload = {
            "email": email,
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
            message=f"OTP has been sent to {email}. Please check.",
            data={"token": jwt_token, "userdata": {"name": user_doc.name}},
        )
    else:
        return ForgotPasswordResponse(
            status=False,
            message=f"This profile does not exist. {email}",
            data={"error": "This profile does not exist."},
        )


@router.post("/change_password", response_model=ChangePasswordResponse, status_code=200)
async def change_password(req: Request,request: ChangePasswordRequest,Authorization: str = Header(None),):
    if Authorization is None:
        return ChangePasswordResponse(
            status=False,
            message="Authorization header is missing",
            data={"error": "Please provide an Authorization header."},
        )
    
    jwt_token = await login_checker(Authorization=Authorization)
    decoded_payload = jwt_token_checker(jwt_token=jwt_token, encode=False)
    user_email = decoded_payload["email"]
    user_doc=await sync_to_async(UserManagement.objects.filter(email=user_email).first)()

    if user_doc is None:
        return ChangePasswordResponse(
            status=False,
            message="This profile does not exist.",
            data={"error": "This profile does not exist."},
        )

    if password_checker(request.old_password,user_doc.password):
        user_doc.password = password_encoder(request.password)
        user_doc.updated_at = timezone.now()
        await sync_to_async(user_doc.save)()

        return ChangePasswordResponse(
            status=True,
            message="Your password has been reset successfully!",
            data={}
        )
    else:
        return ChangePasswordResponse(
            status=False,
            message="Password update failed",
            data={"error": "Old Password didn't match. Please provide the correct Old Password."},
            status_code=403
        )