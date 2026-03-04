import os

from celery import Celery

from config import celery_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

celery_app = Celery(
    celery_settings.celery_main,
    broker=celery_settings.celery_broker,
    backend=celery_settings.celery_backend,
)

celery_app.config_from_object(celery_settings)
celery_app.autodiscover_tasks()
