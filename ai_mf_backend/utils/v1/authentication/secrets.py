from typing import Annotated, Dict, Union

import jwt

from asgiref.sync import sync_to_async

from fastapi import Header

from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password

from phonenumber_field.validators import validate_international_phonenumber
from datetime import datetime, timezone

from ai_mf_backend.config.v1.authentication_config import authentication_config
from ai_mf_backend.utils.v1.errors import (
    MalformedJWTRequestException,
)
from ai_mf_backend.models.v1.database.user import UserContactInfo


def jwt_token_checker(
    payload: Dict = None, jwt_token: str = None, encode: bool = True
) -> Union[str, Dict]:
    """
    This method can perform various operations on the JWT token.
    :param payload: payload that needs to be encoded
    :param jwt_token: token that needs to be decoded
    :param encode: boolean on whether we want to encode a payload or decode a token
    :return: a string of encoded payload or a dict of decoded jwt string
    :raises: when the combinations are not correct
    """
    if encode and payload:
        # Encoding a new JWT
        try:
            encode_jwt = jwt.encode(
                payload, authentication_config.SECRET, algorithm="HS256"
            )
            return encode_jwt
        except Exception as e:
            raise MalformedJWTRequestException(f"Error encoding JWT: {e}")

    elif not encode and jwt_token:
        # Decoding an existing JWT
        try:
            # Strip 'Bearer ' prefix if present
            if "Bearer" in jwt_token:
                jwt_token = jwt_token.split("Bearer ")[1].strip()

            # Fix padding if needed
            padding_needed = len(jwt_token) % 4
            if padding_needed != 0:
                jwt_token += '=' * (4 - padding_needed)

            # Decode the JWT without expiration claim check
            decoded_jwt = jwt.decode(
                jwt_token, authentication_config.SECRET, algorithms=["HS256"], options={"verify_exp": False}
            )

            # Manually check the expiry field
            expiry = decoded_jwt.get("expiry")
            if expiry and datetime.now(timezone.utc).timestamp() > expiry:
                raise MalformedJWTRequestException("Error decoding JWT: Token has expired.")

            return decoded_jwt
        except Exception as e:
            raise MalformedJWTRequestException(f"Error decoding JWT: {e}")

    else:
        raise MalformedJWTRequestException("Malformed JWT request: No valid input provided")


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
    hashed = make_password(password=password)
    return hashed  # Return as a string


def password_checker(plain_password: str, hashed_password: str) -> bool:
    """
    This method checks if a given password matches the hashed password.
    :param plain_password: the plain text password to check
    :param hashed_password: the hashed password stored in the database
    :return: True if the passwords match, False otherwise
    """
    return check_password(password=plain_password, encoded=hashed_password)


async def login_checker(Authorization: Annotated[str | None, Header()]):

    if not Authorization:
        raise MalformedJWTRequestException(
            "A Valid token is required to work with this request"
        )

    decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)

    if decoded_payload["token_type"] != "login":
        raise MalformedJWTRequestException(
            "Login token type is required to work with this request"
        )

    email = decoded_payload.get("email")
    mobile_no = decoded_payload.get("mobile_number")

    if not any([email, mobile_no]):
        raise MalformedJWTRequestException(
            "A Valid token is required to work with this request 1"
        )

    if all([email, mobile_no]):
        raise MalformedJWTRequestException(
            "A Valid token is required to work with this request 2"
        )

    if email:
        try:
            _ = validate_email(value=email)
        except ValidationError as error_response:
            raise MalformedJWTRequestException(
                f"A Valid token is required to work with this request -> {error_response}"
            )

    elif mobile_no:
        # We expect the number to be of the format +91 8389273829
        try:
            _ = validate_international_phonenumber(value=mobile_no)
        except ValidationError as error_response:
            raise MalformedJWTRequestException(
                f"A Valid token is required to work with this request -> {error_response}"
            )

    if email:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(email=email).first
        )()

    elif mobile_no:
        user_doc = await sync_to_async(
            UserContactInfo.objects.filter(mobile_number=mobile_no).first
        )()

    if not user_doc:
        raise MalformedJWTRequestException("This user does not exist.")

    expiry = float(decoded_payload["expiry"])
    current_time = float(timezone.now().timestamp())
    if current_time < expiry:
        return Authorization
    else:
        raise MalformedJWTRequestException("The provided Auth token has expired")
