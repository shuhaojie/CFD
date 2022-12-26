from asgiref.sync import async_to_sync
from celery import Celery
from apps.task.tasks import monitor_task

celery = Celery("CFD")
celery.conf.broker_url = f"redis://localhost:6379"
celery.conf.result_backend = f"redis://localhost:6379"


@celery.task(name="run_task")
def run_task(task_id):
    async_to_sync(monitor_task)(task_id)
