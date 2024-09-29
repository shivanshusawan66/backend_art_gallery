from enum import Enum


class APIConstants(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class SignUpType(Enum):
    otp = "otp"
    password = "password"
