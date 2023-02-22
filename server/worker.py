import asyncio
import traceback
from asgiref.sync import async_to_sync
from celery import Celery
from apps.task.tasks import monitor_task
from config import configs
from logs import api_log

celery = Celery("CFD")
if configs.ENVIRONMENT == 'local':
    celery.conf.broker_url = f"redis://{configs.REDIS_HOST}/0"
    celery.conf.result_backend = f"redis://{configs.REDIS_HOST}/0"
else:
    celery.conf.broker_url = f"redis://:{configs.REDIS_PASSWD}@{configs.REDIS_HOST}/0"
    celery.conf.result_backend = f"redis://:{configs.REDIS_PASSWD}@{configs.REDIS_HOST}/0"


@celery.task(name="run_task")
def run_task(task_id):
    try:
        celery_task_id = run_task.request.id
        loop = asyncio.get_event_loop()
        future = loop.create_task(monitor_task(task_id, celery_task_id))
        loop.run_until_complete(asyncio.wait([future]))
        future.result()
    except Exception as e:
        f = traceback.format_exc()
        api_log.info(e)
        api_log.info(f)
        print(e)
        print(f)
