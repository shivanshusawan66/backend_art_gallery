import asyncio
from typing import Optional, List

# from pydantic import field_validator

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

    DEFAULT_ALL_MF_DISPLAY_COLUMNS: Optional[List[str]] = [
        "fund_id",
        "scheme_name",
        "morningstar_rating",
        "fund_family",
        "net_asset_value",
        "min_investment",
        "category",
    ]

    # Default page size and validation constants
    DEFAULT_PAGE: Optional[int] = 1
    DEFAULT_PAGE_SIZE: Optional[int] = 10
    MAX_PAGE_SIZE: Optional[int] = 100

    MUTUAL_FUND_OVERVIEW_COLOUMNS: list[str] = [
        "id",
        "scheme_name",
        "q_param",
        "net_asset_value",
        "symbol",
    ]

    MUTUAL_FUND_PERFORMANCE_COLOUMNS: list[str] = [
        "fund_id",
        "ytd_return",
        "average_return_5y",
        "number_of_years_up",
        "number_of_years_down",
        "best_1y_total_return",
        "worst_1y_total_return",
        "best_3y_total_return",
        "worst_3y_total_return",
    ]

    # @field_validator("DEFAULT_DISPLAY_COLUMNS")
    # def validate_default_display_columns(cls, value, **kwargs):
    #     if not isinstance(value, list):
    #         value = [i.strip() for i in value.split(",")]

    #     for i in value:
    #         if i not in COLUMN_MAPPING.keys():
    #             raise Exception(f"Column: {i} is not a valid display column.")
    #     return value


api_config = APIConfig()


class DjangoAppConfig(AppConfig):
    name = api_config.PROJECT_NAME

    def ready(self):
        from ai_mf_backend.utils.v1.constants import refresh_constants

        # Run the asynchronous refresh_constants during startup
        asyncio.run(refresh_constants())
