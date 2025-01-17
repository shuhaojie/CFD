import asyncio
import traceback
from asgiref.sync import async_to_sync
from celery import Celery
from apps.task.tasks import monitor_task
from config import configs
from logs import api_log

celery = Celery("CFD")
if configs.ENVIRONMENT == 'local':
    celery.conf.broker_url = f"redis://:{configs.REDIS_PASSWD}@{configs.REDIS_HOST}/0"
    # celery.conf.result_backend = f"redis://{configs.REDIS_HOST}/0"
else:
    celery.conf.broker_url = f"redis://:{configs.REDIS_PASSWD}@{configs.REDIS_HOST}/0"
    # celery.conf.
    celery.conf.result_backend = f"redis://:{configs.REDIS_PASSWD}@{configs.REDIS_HOST}/1"
# celery.conf.task_ignore_result = True
celery.conf.enable_utc = False
celery.conf.timezone = 'Asia/Shanghai'
celery.conf.broker_heartbeat = 0


def run_task(task_id, md5, username, mac_address, icem_hardware_level, fluent_hardware_level,
             prof, order_id):
    loop = asyncio.new_event_loop()
    future = loop.create_task(
        monitor_task(task_id, md5, username, mac_address, icem_hardware_level, fluent_hardware_level,
                     prof, order_id))
    loop.run_until_complete(asyncio.wait([future]))
    future.result()
