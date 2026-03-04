from django.conf import settings

# from celery.schedules import crontab


celery_main = "backend"
celery_broker = settings.CELERY_BROKER_URL or f"{settings.REDIS_URL}/0"
celery_backend = settings.CELERY_RESULT_URL or f"{settings.REDIS_URL}/0"

task_default_queue = "main"
task_default_exchange = "main"
task_default_routing_key = "main"

task_queues = {
    "main": {
        "exchange": "main",
        "exchange_type": "direct",
        "routing_key": "main",
    },
}

timezone = settings.TIME_ZONE
accept_content = ["application/json", "json", "application/x-python-serialize"]
result_serializer = "pickle"
task_serializer = "pickle"
result_compression = ""
result_expires = 1 * 1 * 60
task_ignore_result = False
task_time_limit = 10 * 60
task_soft_time_limit = task_time_limit - 5
task_acks_late = False
task_acks_on_failure_or_timeout = True
task_reject_on_worker_lost = False
task_track_started = True
broker_transport_options = {
    "visibility_timeout": 60 * 60 * 5,
    "max_retries": 1,
}
result_backend_transport_options = {
    "visibility_timeout": 60 * 60 * 5,
}
task_always_eager = False
task_eager_propagates = False

