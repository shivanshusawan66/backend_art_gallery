from typing import Optional

from ai_mf_backend.config.v1 import BaseSettingsWrapper


class AWSConfig(BaseSettingsWrapper):
    """
    Class for keeping track of all AWS related variables
    """

    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None

    AWS_REGION: Optional[str] = "us-east-1"


aws_config = AWSConfig()
