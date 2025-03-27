from enum import Enum


class APIConstants(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class SignUpType(Enum):
    otp = "otp"
    password = "password"


class ReferenceTableEnums(Enum):
    projection_table_mapping = "projection_table_mapping"
