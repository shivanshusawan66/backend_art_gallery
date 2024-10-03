from typing import Optional

from config.v1 import BaseSettingsWrapper


class APIConfig(BaseSettingsWrapper):
    """
    Configuration class for the API with various API settings

    :param PROJECT_NAME: The name of the project
    :type PROJECT_NAME: str

    :param BACKEND_CORS_ORIGINS: Origins for CORS. If left None, CORS is disabled.
    :type BACKEND_CORS_ORIGINS: Optional[str]

    :param API_VER_STR_V1: Version string for the API
    :type API_VER_STR_V1: str

    :returns: Instance of APIConfig with specific settings
    :return type: APIConfig
    """

    PROJECT_NAME: str = "ai-mf-backend"
    BACKEND_CORS_ORIGINS: Optional[str] = None
    API_VER_STR_V1: str = "/api/v1"


api_config = APIConfig()
