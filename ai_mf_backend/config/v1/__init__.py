import os

from pydantic_settings import BaseSettings


class BaseSettingsWrapper(BaseSettings):
    class Config:
        env_file = (
            "ai_mf_backend/.env" if os.path.exists("ai_mf_backend/.env") else ".env"
        )
        case_sensitive = True
        extra = "allow"
