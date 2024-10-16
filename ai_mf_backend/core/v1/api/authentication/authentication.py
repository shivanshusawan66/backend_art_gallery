import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Response


from ai_mf_backend.models.v1.database.user_authentication import UserLogs
from ai_mf_backend.utils.v1.authentication.otp import send_email_otp
from ai_mf_backend.utils.v1.authentication.secrets import (
    jwt_token_checker,
    password_checker,
    password_encoder,
)
from ai_mf_backend.models.v1.database.user import (
    UserContactInfo,
    OTPlogs,
    
)
from asgiref.sync import sync_to_async
from django.utils import timezone
from fastapi.responses import RedirectResponse

from ai_mf_backend.models.v1.api.user_authentication import (
    Sign_up_in_password_request,
    Sign_up_in_password_response,
    Auth_OTP_Request,
    Auth_OTP_Response
)
logger = logging.getLogger(__name__)
router = APIRouter()



@router.post(
    "/sign_up_in_password",
    status_code=200,
)
async def sign_up_in_password(request: Sign_up_in_password_request):
    email=request.email
    mobile_no=request.mobile_no
    password=request.password

    if email:
        user_doc = await sync_to_async(UserContactInfo.objects.filter(email=email).first)()
        print(email)
    elif mobile_no:
        user_doc = await sync_to_async(UserContactInfo.objects.filter(mobile_number=mobile_no).first)()
        print(mobile_no)
    else:
        return Sign_up_in_password_response(
            status=False,
            message="Invalid email or mobile number",
            data={},
            status_code=404,
        )
      
    if user_doc and user_doc.password:
        if password_checker(password, user_doc.password):
            if user_doc.email:
                new_payload = {
                    "email": user_doc.email,
                    "token_type": "logged_in",
                    "creation_time": timezone.now().timestamp(),
                    "expiry": (
                        (
                            timezone.now() + timedelta(hours=5)
                        ).timestamp()  # Fixed to 5 hours
                        if not request.remember_me
                        else (timezone.now() + timedelta(days=365)).timestamp()
                    ),
                }
            else:
                new_payload = {
                    "mobile_number": user_doc.mobile_number,
                    "token_type": "logged_in",
                    "creation_time": timezone.now().timestamp(),
                    "expiry": (
                        (
                            timezone.now() + timedelta(hours=5)
                        ).timestamp()  # Fixed to 5 hours
                        if not request.remember_me
                        else (timezone.now() + timedelta(days=365)).timestamp()
                    ),
                }
            jwt_token = jwt_token_checker(payload=new_payload, encode=True)

            user_logs = UserLogs(
                user=user_doc,
                ip_details=request.ip_details,
                device_type=request.device_type,
                last_access=timezone.now(),
                action="logged_in",
            )

            await sync_to_async(user_logs.save)()
            return Sign_up_in_password_response(
                status=True,
                message=f"Successfully logged in to the Dashboard",
                data={"token": jwt_token, "userdata": {"email_or_mobile_no": email if email else mobile_no}},
            )
        else:
            return Sign_up_in_password_response(
                status=False,
                message=f"Please check your id password",
                data={"email": "Invalid login credentials."},
                status_code=403,
            )
    elif user_doc and not user_doc.password :
        return Sign_up_in_password_response(
            status=False,
            message=f"User found but you have to login though otp as you have done in the past",
            data={"email_or_mobile_no": email if email else mobile_no},
            status_code=404,
        )
    else:
        password = password_encoder(password=password)
        user_doc = UserContactInfo(
                email=email,
                mobile_number=mobile_no,
                password=password,
            )
        await sync_to_async(user_doc.save)()

        user_otp=OTPlogs(
            user=user_doc,
            )
        
        await sync_to_async(user_otp.save)()

        user_logs = UserLogs(
                user=user_doc,
                ip_details=request.ip_details,
                device_type=request.device_type,
                last_access=timezone.now(),
                action="signed_up",
            )
        await sync_to_async(user_logs.save)()
        if email: 
            payload = {
                "email": email ,
                "token_type": "signup",
                "creation_time": timezone.now().timestamp(),
                "expiry": (
                    (
                        timezone.now() + timedelta(hours=5)
                    ).timestamp()  # Fixed to 5 hours
                    if not request.remember_me
                    else (timezone.now() + timedelta(days=365)).timestamp()
                ),
            }
        else:
            payload = {
                "mobile_number": mobile_no,
                "token_type": "signup",
                "creation_time": timezone.now().timestamp(),
                "expiry": (
                    (
                        timezone.now() + timedelta(hours=5)
                    ).timestamp()  # Fixed to 5 hours
                    if not request.remember_me
                    else (timezone.now() + timedelta(days=365)).timestamp()
                ),
            }
        jwt_token = jwt_token_checker(payload=payload, encode=True)
        return Sign_up_in_password_response(
            status=True,
            message=f"welcome you are the first time time user",
            data={"token": jwt_token, "userdata": {"email_or_mobile_no": email if email else mobile_no}},
        )
        

@router.post(
    "/auth_send_otp",
    status_code=200,
)
async def auth_otp(request: Auth_OTP_Request):
    email=request.email
    mobile_no=request.mobile_no


    if email:
        user_doc = await sync_to_async(UserContactInfo.objects.filter(email=email).first)()
    elif mobile_no:
        user_doc = await sync_to_async(UserContactInfo.objects.filter(mobile_number=mobile_no).first)()
    else:
        return Auth_OTP_Response(
            status=False,
            message="Invalid email or mobile number",
            data={"email_or_mobile_no": "Invalid login credentials."},
            status_code=404,
        )
    
    if user_doc :
        user_otp=await sync_to_async(
            OTPlogs.objects.filter(user=user_doc.user_id).first
            )()
        if user_otp:
            otp=send_email_otp()
    
            user_otp.otp=otp
            user_otp.otp_valid=timezone.now() + timedelta(minutes=15)
            await sync_to_async(user_otp.save)()
        else:
            return Auth_OTP_Response(
                status=False,
                message="User Exist, but OTP table does not",
                data={"email_or_mobile_no": email if email else mobile_no,
                    }
                )
        if user_doc.email:
            new_payload = {
                "email": user_doc.email,
                "token_type": "logged_in",
                "creation_time": timezone.now().timestamp(),
                "expiry": (
                    (
                        timezone.now() + timedelta(hours=5)
                    ).timestamp()  # Fixed to 5 hours
                    if not request.remember_me
                    else (timezone.now() + timedelta(days=365)).timestamp()
                ),
            }
        else:
            new_payload = {
                "mobile_number": user_doc.mobile_number,
                "token_type": "logged_in",
                "creation_time": timezone.now().timestamp(),
                "expiry": (
                    (
                        timezone.now() + timedelta(hours=5)
                    ).timestamp()  # Fixed to 5 hours
                    if not request.remember_me
                    else (timezone.now() + timedelta(days=365)).timestamp()
                ),
            }
        jwt_token = jwt_token_checker(payload=new_payload, encode=True)

        response = Auth_OTP_Response(
            status=True,
            message=f"OTP successfully send to user ",
            data={"token": jwt_token, "userdata": { "email_or_mobile_no": user_doc.email if email else user_doc.mobile_number},
                    'otp':otp}
        )
        return response
    else:
        user_doc = UserContactInfo(
            email=email,
            mobile_number=mobile_no
        )
        await sync_to_async(user_doc.save)()
        
        otp=send_email_otp()

        user_otp=OTPlogs(
            user=user_doc,
            otp=otp,
            otp_valid=timezone.now() + timedelta(minutes=15)
            )
        await sync_to_async(user_otp.save)()

        if user_doc.email:
            new_payload = {
                "email": user_doc.email,
                "token_type": "logged_in",
                "creation_time": timezone.now().timestamp(),
                "expiry": (
                    (
                        timezone.now() + timedelta(hours=5)
                    ).timestamp()  # Fixed to 5 hours
                    if not request.remember_me
                    else (timezone.now() + timedelta(days=365)).timestamp()
                ),
            }
        else:
            new_payload = {
                "mobile_number": user_doc.mobile_number,
                "token_type": "logged_in",
                "creation_time": timezone.now().timestamp(),
                "expiry": (
                    (
                        timezone.now() + timedelta(hours=5)
                    ).timestamp()  # Fixed to 5 hours
                    if not request.remember_me
                    else (timezone.now() + timedelta(days=365)).timestamp()
                ),
            }
        jwt_token = jwt_token_checker(payload=new_payload, encode=True)

        response = Auth_OTP_Response(
            status=True,
            message=f"OTP successfully send to newly created user ",
            data={"token": jwt_token, "userdata": { "email_or_mobile_no": user_doc.email if email else user_doc.mobile_number},
                    'otp':otp}
        )
        return response
        