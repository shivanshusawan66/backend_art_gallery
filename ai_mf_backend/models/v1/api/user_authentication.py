from typing import Optional, Dict
from pydantic import BaseModel
from enum import Enum

from ai_mf_backend.models.v1.api import Response


class Sign_up_in_password_request(BaseModel):
    email: Optional[str] = ""
    mobile_no: Optional[str] = ""
    password: str
    remember_me: Optional[bool] = False
    device_type: Optional[str] = ""
    ip_details: Optional[Dict] = dict()


class Sign_up_in_password_response(Response):
    pass


class Auth_OTP_Request(BaseModel):
    email: Optional[str] = ""
    mobile_no: Optional[str] = ""
    remember_me: Optional[bool] = False
    device_type: Optional[str] = ""
    ip_details: Optional[Dict] = dict()


class Auth_OTP_Response(Response):
    pass


class ForgotPasswordRequest(BaseModel):
    email: Optional[str] = ""
    mobile_no: Optional[str] = ""


class ForgotPasswordResponse(Response):
    pass


class ChangePasswordRequest(BaseModel):
    token: str
    old_password: str
    password: str


class ChangePasswordResponse(Response):
    pass


class OTPVerificationRequest(BaseModel):
    otp: int
    token: str
    password: Optional[str] = ""


class OTPVerificationResponse(Response):
    pass


class ResendOTPRequest(BaseModel):
    email: Optional[str] = ""
    mobile_no: Optional[str] = ""


class ResendOTPResponse(Response):
    pass
