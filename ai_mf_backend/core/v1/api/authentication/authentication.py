import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Response

from ai_mf_backend.app.schemas.v1.authentication import (
    loginResponse,
    LoginRequest,
    SignUpRequest,
    SignUpResponse,
)
from ai_mf_backend.app.models import UserLogs
from ai_mf_backend.app.models import UserManagement
from ai_mf_backend.utils.v1.authentication.otp import send_email_otp
from ai_mf_backend.utils.v1.authentication.secrets import (
    jwt_token_checker,
    password_checker,
    password_encoder,
)
from asgiref.sync import sync_to_async
from django.utils import timezone
from fastapi.responses import RedirectResponse


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/signup_otp", status_code=200)
async def signup_otp(request: LoginRequest, response: Response):

    if request.email:
        doc = await sync_to_async(
            UserManagement.objects.filter(email=request.email).first
        )()
        current_time = timezone.now()
        if doc:
            if current_time < doc.otp_valid_till:
                if request.otp == doc.otp:
                    new_payload = {
                        "email": doc.email,
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
                    doc.last_access = timezone.now()
                    await sync_to_async(doc.save)()

                    user_logs = UserLogs(
                        email_id=request.email,
                        ip_details=request.ip_details,
                        device_type=request.device_type,
                        last_access=timezone.now(),
                        action="logged_in",
                    )

                    await sync_to_async(user_logs.save)()

                    response = loginResponse(
                        status=True,
                        message=f"Successfully logged in to the Dashboard",
                        data={"token": jwt_token, "userdata": {"name": doc.email}},
                    )
                    return response
                else:
                    response = loginResponse(
                        status=False,
                        message=f"Invalid OTP",
                        data={"email": f"{request.email}"},
                    )
                    return response
            else:
                response = loginResponse(
                    status=False,
                    message=f"OTP expired",
                    data={"email": f"{request.email}"},
                )
                return response
        else:
            response = loginResponse(
                status=False,
                message=f"This account does not exist.",
                data={"email": "This account does not exist."},
            )
            response.status_code = 403
            return response

    elif request.mobile_no:
        doc = await sync_to_async(
            UserManagement.objects.filter(mobile_number=request.mobile_no).first
        )()
        current_time = timezone.now()
        if doc:
            if current_time < doc.otp_valid_till:
                if request.otp == doc.otp:
                    new_payload = {
                        "mobile_no": doc.mobile_number,
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
                    doc.last_access = timezone.now()
                    await sync_to_async(doc.save)()

                    user_logs = UserLogs(
                        mobile_number=request.mobile_no,
                        ip_details=request.ip_details,
                        device_type=request.device_type,
                        last_access=timezone.now(),
                        action="logged_in",
                    )

                    await sync_to_async(user_logs.save)()

                    response = loginResponse(
                        status=True,
                        message=f"Successfully logged in to the Dashboard",
                        data={
                            "token": jwt_token,
                            "userdata": {"name": doc.mobile_number},
                        },
                    )
                    return response
                else:
                    response = loginResponse(
                        status=False,
                        message=f"Invalid OTP",
                        data={"mobile_number": f"{request.mobile_no}"},
                    )
                    return response
            else:
                response = loginResponse(
                    status=False,
                    message=f"OTP expired",
                    data={"mobile_number": f"{request.mobile_no}"},
                )
                return response
        else:
            response = loginResponse(
                status=False,
                message=f"This account does not exist.",
                data={"email": "This account does not exist."},
            )
            response.status_code = 403
            return response


@router.post(
    "/signup",
    status_code=200,
)
async def signup(request: SignUpRequest, response: Response):

    email = request.email
    password = request.password
    mobile_no = request.mobile_no

    # user_doc = await sync_to_async(UserManagement.objects.filter(email=request.email).first)()

    if email and password and request.type == "password":
        user_doc = await sync_to_async(
            UserManagement.objects.filter(email=email).first
        )()
        if user_doc:
            if not user_doc.password:
                return SignUpResponse(
                    status=False,
                    message=f"please login through otp",
                    data={"mobile_number": f"{mobile_no}"},
                    status_code=403,
                )
            elif password_checker(password, user_doc.password):
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

                jwt_token = jwt_token_checker(payload=new_payload, encode=True)
                user_doc.last_access = timezone.now()
                await sync_to_async(user_doc.save)()

                user_logs = UserLogs(
                    email_id=request.email,
                    ip_details=request.ip_details,
                    device_type=request.device_type,
                    last_access=timezone.now(),
                    action="logged_in",
                )

                await sync_to_async(user_logs.save)()
                return SignUpResponse(
                    status=True,
                    message=f"Successfully logged in to the Dashboard",
                    data={"token": jwt_token, "userdata": {"name": user_doc.email}},
                )
            else:
                return SignUpResponse(
                    status=False,
                    message=f"Please check your id password",
                    data={"email": "Invalid login credentials."},
                    status_code=403,
                )
        else:
            password = password_encoder(password=password)
            user_doc = UserManagement(
                email=email,
                password=password,
                created_at=timezone.now(),
            )
            await sync_to_async(user_doc.save)()

            payload = {
                "email": email,
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

            return SignUpResponse(
                status=True,
                message=f"welcome you are the first time time user",
                data={"token": jwt_token, "userdata": {"email": email}},
            )

    elif mobile_no and password and request.type == "password":
        user_doc = await sync_to_async(
            UserManagement.objects.filter(mobile_number=mobile_no).first
        )()
        if user_doc:
            if not user_doc.password:
                return SignUpResponse(
                    status=False,
                    message=f"please login through otp",
                    data={"mobile_number": f"{mobile_no}"},
                    status_code=403,
                )
            elif password_checker(password, user_doc.password):
                new_payload = {
                    "mobile_no": user_doc.mobile_number,
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
                user_doc.last_access = timezone.now()
                await sync_to_async(user_doc.save)()

                user_logs = UserLogs(
                    mobile_number=mobile_no,
                    ip_details=request.ip_details,
                    device_type=request.device_type,
                    last_access=timezone.now(),
                    action="logged_in",
                )
                await sync_to_async(user_logs.save)()

                return SignUpResponse(
                    status=True,
                    message=f"Successfully logged in to the Dashboard",
                    data={
                        "token": jwt_token,
                        "userdata": {"mobile": user_doc.mobile_number},
                    },
                )
            else:
                return SignUpResponse(
                    status=False,
                    message=f"Please check your id password",
                    data={"email": "Invalid login credentials."},
                    status_code=403,
                )
        else:
            password = password_encoder(password=password)
            user_doc = UserManagement(
                mobile_number=mobile_no,
                password=password,
                created_at=timezone.now(),
            )
            await sync_to_async(user_doc.save)()

            payload = {
                "mobile_no": mobile_no,
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
            return SignUpResponse(
                status=True,
                message=f"welcome you are the first time time user",
                data={"token": jwt_token, "userdata": {"mobile": mobile_no}},
            )
    elif email and request.type == "otp":
        user_doc = await sync_to_async(
            UserManagement.objects.filter(email=email).first
        )()
        if user_doc:
            otp = send_email_otp()
            print(otp)
            user_doc.otp = otp
            user_doc.otp_valid_till = timezone.now() + timedelta(minutes=15)
            await sync_to_async(user_doc.save)()
            return RedirectResponse(url="/signup_otp", status_code=302)
        else:
            otp = send_email_otp()
            user_doc = UserManagement(
                email=email,
                created_at=timezone.now(),
                otp=otp,
                otp_valid_till=timezone.now() + timedelta(minutes=15),
            )
            await sync_to_async(user_doc.save)()
            return RedirectResponse(url="/signup_otp", status_code=302)
    elif mobile_no and request.type == "otp":
        user_doc = await sync_to_async(
            UserManagement.objects.filter(mobile_number=mobile_no).first
        )()
        if user_doc:
            otp = send_email_otp()
            user_doc.otp = otp
            user_doc.otp_valid_till = timezone.now() + timedelta(minutes=15)
            await sync_to_async(user_doc.save)()
            return RedirectResponse(url="/signup_otp", status_code=302)
        else:
            otp = send_email_otp()
            user_doc = UserManagement(
                mobile_number=mobile_no,
                created_at=timezone.now(),
                otp=otp,
                otp_valid_till=timezone.now() + timedelta(minutes=15),
            )
            await sync_to_async(user_doc.save)()
            return RedirectResponse(url="/signup_otp", status_code=302)
