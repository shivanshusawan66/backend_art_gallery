from typing import Optional, Dict
from pydantic import BaseModel
from enum import Enum

from ai_mf_backend.models.v1.api import Response


class SignUpType(str, Enum):
    otp = "otp"
    password = "password"


class LoginRequest(BaseModel):
    email: Optional[str] = ""
    mobile_no: Optional[str] = ""
    otp: Optional[int]
    remember_me: Optional[bool] = False
    device_type: Optional[str] = ""
    ip_details: Optional[Dict] = dict()


class loginResponse(Response):
    pass


class SignUpRequest(BaseModel):
    email: Optional[str] = ""
    password: Optional[str] = ""
    mobile_no: Optional[str] = ""
    remember_me: Optional[bool] = False
    device_type: Optional[str] = ""
    ip_details: Optional[Dict] = dict()
    type: SignUpType


class SignUpResponse(Response):
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
