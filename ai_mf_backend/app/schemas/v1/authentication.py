from typing import Optional,Dict
from pydantic import BaseModel

from app.schemas.v1 import Response

class LoginRequest(BaseModel):
    email:str
    password:str
    remember_me:Optional[bool]=False
    device_type:Optional[str]=""
    ip_details:Optional[Dict]=dict()


class loginResponse(Response):
    pass

class SignUpRequest(BaseModel):
    email: str
    password: str
    name: str

class SignUpResponse(Response):
    pass 

class ForgotPasswordRequest(BaseModel):
    email: str

class ForgotPasswordResponse(Response):
    pass 


class ChangePasswordRequest(BaseModel):
    email: Optional[str]=""
    old_password: str
    password: str

class ChangePasswordResponse(Response):
    pass 

class OTPVerificationRequest(BaseModel):
    otp: int
    token: str
    password: Optional[str]=""

class OTPVerificationResponse(Response):
    pass  

class ResendOTPRequest(BaseModel):
    token: str

class ResendOTPResponse(Response):
    pass