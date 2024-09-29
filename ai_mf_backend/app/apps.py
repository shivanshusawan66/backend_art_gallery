from django.apps import AppConfig

from ai_mf_backend.config.v1.api_config import api_config


class AiMfBackendConfig(AppConfig):
    name = api_config.PROJECT_NAME
