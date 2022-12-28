from asgiref.sync import async_to_sync
from celery import Celery
from apps.task.tasks import monitor_task
from config import configs

celery = Celery("CFD")
if configs.ENVIRONMENT == 'local':
    celery.conf.broker_url = f"redis://{configs.REDIS_HOST}/0"
    celery.conf.result_backend = f"redis://{configs.REDIS_HOST}/0"
else:
    celery.conf.broker_url = f"redis://:{configs.REDIS_PASSWD}@{configs.REDIS_HOST}/0"
    celery.conf.result_backend = f"redis://:{configs.REDIS_PASSWD}@{configs.REDIS_HOST}/0"


@celery.task(name="run_task")
def run_task(task_id):
    celery_task_id = run_task.request.id
    async_to_sync(monitor_task)(task_id, celery_task_id)
