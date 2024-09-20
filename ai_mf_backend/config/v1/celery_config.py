from pydantic import field_validator

from config.v1 import BaseSettingsWrapper


class CeleryConfig(BaseSettingsWrapper):
    """
    Class for keeping track of all celery related variables
    """

    CELERY_BROKER_URL: str = "redis://redis:6379"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379"
    CELERY_ENABLE_UTC: int = 0
    CELERY_TIMEZONE: str = "UTC"

    @field_validator("CELERY_ENABLE_UTC", mode="after")
    def set_enable_utc(cls, CELERY_ENABLE_UTC: int):
        return True if CELERY_ENABLE_UTC == 1 else 0


celery_config = CeleryConfig()
