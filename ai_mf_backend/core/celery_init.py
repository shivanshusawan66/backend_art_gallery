from celery import Celery


from ai_mf_backend.config.v1.celery_config import celery_config

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
