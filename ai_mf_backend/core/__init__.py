import os
import logging
import django

from fastapi import APIRouter

from celery import Celery
from celery.schedules import crontab

from ai_mf_backend.config.v1.celery_config import celery_config


from ai_mf_backend.utils.v1.connections import create_connections, check_connections

logger = logging.getLogger(__name__)

create_connections()
check_connections()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)

django.setup()

connect_router = APIRouter()

celery_app = Celery(
    "tasks",
    broker=celery_config.CELERY_BROKER_URL,
    backend=celery_config.CELERY_RESULT_BACKEND,
)

celery_app.control.purge()
celery_app.conf.CELERY_WORKER_REDIRECT_STDOUTS = False
celery_app.conf.worker_redirect_stdouts = False
celery_app.conf.accept_content = ["pickle", "json"]

celery_app.conf.task_serializer = "pickle"
celery_app.conf.result_serializer = "pickle"

celery_app.conf.enable_utc = False
celery_app.conf.timezone = "Asia/Kolkata"


celery_app.conf.beat_schedule = {
    "run-all-apis-every-day-23-31": {
        "task": "ai_mf_backend.core.v1.tasks.fetching_data.run_all_apis",
        "schedule": crontab(hour=23, minute=32),
    }
}
