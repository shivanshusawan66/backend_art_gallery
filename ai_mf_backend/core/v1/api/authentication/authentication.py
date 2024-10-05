import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Response

from ai_mf_backend.models.v1.api.user_authentication import (
    loginResponse,
    LoginRequest,
    SignUpRequest,
    SignUpResponse,
)
from ai_mf_backend.models.v1.database.user_authentication import UserLogs
from ai_mf_backend.models.v1.database.user_authentication import UserManagement
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
    """
    Handles user login via OTP (One-Time Password) for email or mobile number.

    This endpoint validates a user's OTP for account login using either an email or a mobile number.
    It also generates a JWT token upon successful login and logs the user's login activities.

    The OTP is checked against the `UserManagement` database to ensure the OTP is valid and unexpired.

    Parameters:
    ----------
    request : LoginRequest
        A Pydantic model instance containing the user's email or mobile number, OTP,
        `remember_me` flag, IP details, and device type.

    response : Response
        A FastAPI response object used to return the login response.

    Logic:
    ------
    1. If the user provides an email:
       - Fetches the corresponding `UserManagement` record.
       - Checks if the OTP is still valid (before expiration).
       - If valid, compares the OTP provided by the user with the one in the database.
       - If the OTP matches:
         - Generates a JWT token with a 5-hour expiry (or 365 days if `remember_me` is enabled).
         - Updates the `last_access` time of the user.
         - Logs the login action in the `UserLogs` model.
         - Returns a success response with the JWT token.
       - If the OTP does not match or is expired, returns an appropriate error response.
       - If no account is found with the provided email, returns a 403 response.

    2. If the user provides a mobile number:
       - Follows a similar flow as the email logic but uses the mobile number for fetching the account.
       - The same validation, token generation, and logging logic is applied for mobile number login.

    Returns:
    --------
    loginResponse : JSON
        A structured response indicating whether the login was successful or failed.
        Includes the JWT token and user data in case of success, or an error message in case of failure.

    Possible Status Codes:
    ----------------------
    - 200: Successful login (JWT token returned).
    - 403: Account does not exist.

    Example:
    --------
    Request:
        POST /signup_otp
        {
            "email": "user@example.com",
            "otp": "123456",
            "remember_me": false,
            "ip_details": "192.168.1.1",
            "device_type": "web"
        }

    Response:
        {
            "status": true,
            "message": "Successfully logged in to the Dashboard",
            "data": {
                "token": "jwt_token",
                "userdata": {
                    "name": "user@example.com"
                }
            }
        }
    """

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
    """
    Handles user signup and login through email or mobile number with support for both password-based
    and OTP (One-Time Password) authentication.

    This endpoint facilitates user authentication through two types:
    1. Password-based authentication.
    2. OTP-based authentication.

    If the user logs in with a password, the system will check if the user already exists, validate their
    password, and generate a JWT token if the credentials are correct. If the user signs up for the first time,
    a new account will be created, a JWT token will be generated, and the login logs will be updated.

    For OTP-based authentication, the system generates an OTP and redirects the user to an OTP verification
    endpoint (`/signup_otp`).

    Parameters:
    -----------
    request : SignUpRequest
        A Pydantic model instance containing the user's signup details, such as email, mobile number, password,
        authentication type (`password` or `otp`), IP details, device type, and `remember_me` flag.

    response : Response
        A FastAPI response object used to return the signup/login response.

    Logic:
    ------
    1. **Password-based Authentication** (`type == 'password'`):
       - **Email-based**:
         - If an email and password are provided, it checks whether the user exists.
         - If the user exists but has no password, prompts the user to login via OTP.
         - If the user exists with a password, verifies the password and logs in if correct.
         - Generates a JWT token with an expiry of 5 hours (or 365 days if `remember_me` is set).
         - Logs the login action and returns the JWT token.
         - If the user does not exist, creates a new account with the provided password and generates a JWT token.
       - **Mobile number-based**:
         - Follows a similar process as email-based login but checks the mobile number for user existence.

    2. **OTP-based Authentication** (`type == 'otp'`):
       - **Email-based**:
         - If an email is provided and OTP is requested, it checks whether the user exists.
         - If the user exists, generates an OTP and stores it in the `UserManagement` model, valid for 15 minutes.
         - If the user does not exist, creates a new user record and sends an OTP.
         - Redirects to `/signup_otp` for OTP verification.
       - **Mobile number-based**:
         - Similar logic applies for mobile number OTP generation and redirection to `/signup_otp`.

    Returns:
    --------
    SignUpResponse or RedirectResponse: JSON
        A structured response indicating the outcome of the signup/login process.
        Includes the JWT token in case of successful login, or redirects to OTP verification page.

    Possible Status Codes:
    ----------------------
    - 200: Successful login (JWT token returned).
    - 302: Redirect to OTP verification.
    - 403: Invalid credentials or OTP-required login.

    Example:
    --------
    **Password-based Login**:
    Request:
        POST /signup
        {
            "email": "user@example.com",
            "password": "password123",
            "type": "password",
            "remember_me": true,
            "ip_details": "192.168.1.1",
            "device_type": "web"
        }

    Response:
        {
            "status": true,
            "message": "Successfully logged in to the Dashboard",
            "data": {
                "token": "jwt_token",
                "userdata": {
                    "name": "user@example.com"
                }
            }
        }

    **OTP-based Signup**:
    Request:
        POST /signup
        {
            "email": "user@example.com",
            "type": "otp",
            "ip_details": "192.168.1.1",
            "device_type": "web"
        }

    Response:
        {
            "status_code": 302,
            "redirect": "/signup_otp"
        }
    """
    email = request.email
    password = request.password
    mobile_no = request.mobile_no

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
            user_doc.otp = otp
            user_doc.otp_valid_till = timezone.now() + timedelta(minutes=15)
            await sync_to_async(user_doc.save)()
            return SignUpResponse(
                status=True,
                message=f"We have sent a 6 digit OTP to your email",
                data={"email": email, "otp": otp},
            )
        else:
            otp = send_email_otp()
            user_doc = UserManagement(
                email=email,
                created_at=timezone.now(),
                otp=otp,
                otp_valid_till=timezone.now() + timedelta(minutes=15),
            )
            await sync_to_async(user_doc.save)()
            return SignUpResponse(
                status=True,
                message=f"We have sent a 6 digit OTP to your email",
                data={"email": email, "otp": otp},
            )
    elif mobile_no and request.type == "otp":
        user_doc = await sync_to_async(
            UserManagement.objects.filter(mobile_number=mobile_no).first
        )()
        if user_doc:
            otp = send_email_otp()
            user_doc.otp = otp
            user_doc.otp_valid_till = timezone.now() + timedelta(minutes=15)
            await sync_to_async(user_doc.save)()
            return SignUpResponse(
                status=True,
                message=f"We have sent a 6 digit OTP to your email",
                data={"email": email, "otp": otp},
            )
        else:
            otp = send_email_otp()
            user_doc = UserManagement(
                mobile_number=mobile_no,
                created_at=timezone.now(),
                otp=otp,
                otp_valid_till=timezone.now() + timedelta(minutes=15),
            )
            await sync_to_async(user_doc.save)()
            return SignUpResponse(
                status=True,
                message=f"We have sent a 6 digit OTP to your email",
                data={"email": email, "otp": otp},
            )
