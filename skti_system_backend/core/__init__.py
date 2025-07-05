import os
import logging
import django

from fastapi import APIRouter

from celery import Celery
from celery.schedules import crontab



from skti_system_backend.utils.v1.connections import create_connections, check_connections

logger = logging.getLogger(__name__)

create_connections()
check_connections()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "skti_system_backend.config.v1.django_settings"
)

django.setup()

connect_router = APIRouter()