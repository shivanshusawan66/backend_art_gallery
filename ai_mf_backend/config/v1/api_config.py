from typing import Optional, List

from django.apps import AppConfig

from ai_mf_backend.config.v1 import BaseSettingsWrapper


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

    PROJECT_NAME: str = "ai_mf_backend"
    BACKEND_CORS_ORIGINS: Optional[str] = None
    API_VER_STR_V1: str = "/api/v1"

    REQUEST_PER_MIN: Optional[str] = "20/minute"

    MAX_OTP_REQUESTS: Optional[int] = 20
    THROTTLE_WINDOW_SECONDS: Optional[int] = 300  # 5 mins

    MAX_CHANGES_PER_WINDOW: Optional[int] = 3
    CHANGES_WINDOW: Optional[int] = 7

    OTP_EXPIRATION_DEFAULT_HOURS: Optional[int] = 5
    OTP_EXPIRATION_REMEMBER_DAYS: Optional[int] = 365

    DEFAULT_DISPLAY_COLUMNS: Optional[List[str]] = [
        "fund_id",
        "scheme_name",
        "morningstar_rating",
        "fund_family",
        "net_asset_value",
        "min_investment",
    ]

    # Default page size and validation constants
    DEFAULT_PAGE: Optional[int] = 1
    DEFAULT_PAGE_SIZE: Optional[int] = 10
    MAX_PAGE_SIZE: Optional[int] = 100


api_config = APIConfig()


class DjangoAppConfig(AppConfig):
    name = api_config.PROJECT_NAME
