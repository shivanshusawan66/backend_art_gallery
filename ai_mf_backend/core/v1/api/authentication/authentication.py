import logging
from datetime import datetime,timedelta

from fastapi import APIRouter,Response

from app.schemas.v1.authentication import(loginResponse,LoginRequest,SignUpRequest,SignUpResponse)
from app.models import UserLogs
from app.models import UserManagement
from utils.v1.authentication.otp import send_email_otp
from utils.v1.authentication.secrets import(jwt_token_checker,password_checker,password_encoder)
from asgiref.sync import sync_to_async
from django.utils import timezone

logger=logging.getLogger(__name__)
router=APIRouter()

@router.post("/login",status_code=200)
async def login(request: LoginRequest, response: Response):
    """
    The function used to generate JWT token and login the user
    This function expects password, email, device_type, ip_data, remember_me from payloads.
    Steps:
    -> it will fetch the payload data from post request
    -> it will fetch the user document from user_management_collection
    -> it will encode the password from post request payload for matching it with the database
    -> if the document is found it will check if the password in the payload and the password in the database are same
       or not
        -> if the password matches it will create a jwt encoded payload with the token type
            -> expiry of that token will be 5 hours or 1 year depending on if the user has checked remember me or not
            -> user management collection will be updated with the latest time accessed
            -> user logs will have one document with ip details and device type
    -> if the document is not found, it will 403 stating that user does not exist
    -> else it will return 403 that the credentials were not correct (also the else for if the passwords do not match)
    :return: Response 200 in case user is able to log in
    :return: Response 403 in case user is not able to log in
    """
    password=password_encoder(request.password)
    doc=await sync_to_async(UserManagement.objects.filter(email=request.email).first)()

    if doc:
        if password_checker(request.password, doc.password) and doc.is_verified:
            new_payload={
                "unique_id":str(doc.id),
                "email": doc.email,
                "token_type": "logged_in",
                "creation_time": timezone.now().timestamp(),
                "expiry":(
                    (timezone.now() + timedelta(hours=8)).timestamp()  # Fixed to 5 hours
                    if not request.remember_me
                    else (timezone.now() + timedelta(days=365)).timestamp()
                ),

            }

            jwt_token=jwt_token_checker(payload=new_payload, encode=True)
            doc.last_access=timezone.now()
            await sync_to_async(doc.save)() 

            user_logs=UserLogs(
                name=request.email,
                email_id=request.email,
                ip_details=request.ip_details,
                device_type=request.device_type,
                last_access=timezone.now(),
                action="logged_in"
            )

            await sync_to_async(user_logs.save)() 

            response = loginResponse(
                status=True,
                message=f"Successfully logged in to the Dashboard",
                data={"token": jwt_token, "userdata": {"name": doc.name}},
            )

        elif doc.password == password and not doc.is_verified:
            response = loginResponse(
                status=False,
                message=f"This account is not verified.",
                data={"email": "This account is not verified."},
            )
            response.status_code = 403

        else:
            response = loginResponse(
                status=False,
                message=f"Please check your id password",
                data={"email": "Invalid login credentials."},
            )
            response.status_code = 403
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
    Incase the user does not have an account this method will be helpful in creating the account
    This function expects password, email, name from payloads.
    Steps:
    -> It will load name, email and password from the payload
    -> In case the specified organizations are not present in the email it will return 403
    -> The password from the payload will be encoded for storing in the database
    -> If the user with the email already exists in the database and is verified it will return 409
    -> else it will create a unique id and send an otp to the email
        -> a payload for signup will be generated with 7 days as expiry time.
        -> If the user exists and is not verified the same document will be edited else a new will be inserted with the
           new email, name, password, unique id, OTP generated and OTP expiry time which is 15 mins away from the
           generation time
    :return: Response 200 if account creation is successful
    :return: Response 409 if account already exists
    """
    email=request.email
    password=request.password
    name=request.name

    user_doc= user_doc = await sync_to_async(UserManagement.objects.filter(email=request.email).first)()

    if user_doc and user_doc.is_verified:
        response = SignUpResponse(
            status=False,
            message="User already exists",
            data={"email": "This user already exists."},
        )
        response.status_code = 409

    else:
        password = password_encoder(password=password)

        otp = send_email_otp(receiver_email_id=email)

        if not user_doc:
            user_doc = UserManagement(
                name=name,
                email=email,
                password=password,
                created_at=timezone.now(),
                otp=otp,
                otp_valid_till=timezone.now() + timedelta(minutes=15),
            )
            await sync_to_async(user_doc.save)() 
        else:
            user_doc.name = name
            user_doc.password = password
            user_doc.updated_at = timezone.now()
            user_doc.otp = otp
            user_doc.otp_valid_till = timezone.now() + timedelta(minutes=15)
            await sync_to_async(user_doc.save)() 

        payload = {
            "email": email,
            "name": name,
            "unique_id": str(user_doc.id),
            "token_type": "signup",
            "creation_time": timezone.now().timestamp(),
            "expiry": (timezone.now() + timedelta(days=7)).timestamp(),
        }
        jwt_token = jwt_token_checker(payload=payload, encode=True)

        return SignUpResponse(
            status=True,
            message=f"OTP has been sent to {email}. Please check.",
            data={"token": jwt_token, "userdata": {"name": name}},
        )
    