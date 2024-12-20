import os
import logging

import django

from fastapi import APIRouter

from ai_mf_backend.utils.v1.connections import create_connections, check_connections

logger = logging.getLogger(__name__)

create_connections()
check_connections()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)

django.setup()

connect_router = APIRouter()
