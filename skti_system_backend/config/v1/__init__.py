import os

from pydantic_settings import BaseSettings


class BaseSettingsWrapper(BaseSettings):
    class Config:
        env_file = (
            "skti_system_backend/.env" if os.path.exists("skti_system_backend/.env") else ".env"
        )
        case_sensitive = True
        extra = "allow"
