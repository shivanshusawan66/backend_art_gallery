from typing import Annotated, Dict, Union
from datetime import datetime, timedelta
import jwt
import bcrypt
from fastapi import HTTPException, Header
from django.utils import timezone
from config.v1.authentication_config import authentication_config
from utils.v1.errors import (PasswordNotValidException, MalformedJWTRequestException)
from app.models import (
    UserLogs,UserManagement
)
from asgiref.sync import sync_to_async

def jwt_token_checker(payload: Dict = None, jwt_token: str = None, encode: bool = True) -> Union[str, Dict]:
    """
    This method can perform various operations on the JWT token.
    :param payload: payload that needs to be encoded
    :param jwt_token: token that needs to be decoded
    :param encode: boolean on whether we want to encode a payload or decode a token
    :return: a string of encoded payload or a dict of decoded jwt string
    :raises: when the combinations are not correct
    """
    if encode and payload:
        encode_jwt = jwt.encode(payload, authentication_config.SECRET, algorithm="HS256")
        return encode_jwt

    elif not encode and jwt_token:
        jwt_token = (jwt_token.split("Bearer")[1].strip() if "Bearer" in jwt_token else jwt_token)

        decoded_jwt = jwt.decode(jwt_token, authentication_config.SECRET, algorithms=["HS256"])
        return decoded_jwt

    else:
        raise MalformedJWTRequestException("some problem with the jwt token")

def password_encoder(password: str) -> str:
    """
    This method encodes a password using Bcrypt hashing.
    :param password: password string that needs to be encoded
    :return: a string of hashed password
    :raises: ValueError when the password is not valid
    """
    if not password:
        raise ValueError("Password is not valid")

    # Generate a salt and hash the password
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Return as a string

def password_checker(plain_password: str, hashed_password: str) -> bool:
    """
    This method checks if a given password matches the hashed password.
    :param plain_password: the plain text password to check
    :param hashed_password: the hashed password stored in the database
    :return: True if the passwords match, False otherwise
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

async def login_checker(Authorization: Annotated[str | None, Header()]):
    print("step0")
    if Authorization:
        jwt_token = Authorization
    print("step1")

    if jwt_token:
        decoded_payload = jwt_token_checker(jwt_token=jwt_token, encode=False)
        if decoded_payload['token_type'] != "logged_in":
            raise HTTPException(
                status_code=401,
                detail="Token is not valid for this request.",
            )
        print("step2")
        
        user_log = await sync_to_async(UserLogs.objects.filter(email_id=decoded_payload["email"]).order_by('-last_access').first)()
        print("step3")
        user= await sync_to_async(UserManagement.objects.filter(email=decoded_payload["email"]).first)()
        print("step4")
        if user:
            expiry = float(decoded_payload["expiry"])
            current_time = float(timezone.now().timestamp())
            if current_time < expiry:
                print("step5")
                return Authorization
            else:
                if user_log.action=="logged_in":
                    new_payload = {
                        "unique_id": decoded_payload["email"],
                        "token_type": "logged_in",
                        "expiry": (timezone.now() + timedelta(minutes=30)).timestamp()  # Extend expiry
                    }
                    new_token = jwt_token_checker(payload=new_payload, encode=True)
                    print("step6")
                    return new_token  # Return the new token
                else:
                    print("step7")
                    raise HTTPException(
                        status_code=401,
                        detail="Token is expired, and user is not logged in.",
                    )
        else:
            print("step8")
            raise HTTPException(
                status_code=401,
                detail="This user does not exist.",
            )
    print("step9") 
    raise HTTPException(
        status_code=401,
        detail="No JWT token found.",
    )
