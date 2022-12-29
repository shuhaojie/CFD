import asyncio
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
    # 如果loop关了，要新建一个loop
    if asyncio.get_event_loop().is_closed():
        asyncio.new_event_loop()
        async_to_sync(monitor_task)(task_id, celery_task_id)
    else:
        async_to_sync(monitor_task)(task_id, celery_task_id)
