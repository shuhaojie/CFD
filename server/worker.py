from asgiref.sync import async_to_sync
from celery import Celery
from apps.task.tasks import monitor_task
from config import configs

celery = Celery("CFD")
celery.conf.broker_url = f"redis://:{configs.REDIS_PASSWORD}{configs.REDIS_HOST}/0"
celery.conf.result_backend = f"redis://:{configs.REDIS_PASSWORD}{configs.REDIS_HOST}/0"


@celery.task(name="run_task")
def run_task(task_id):
    async_to_sync(monitor_task)(task_id)
