import os
import sys
import json
import requests
import subprocess
from tortoise import Tortoise, run_async
import datetime
import os
import pytz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from dbs.database import TORTOISE_ORM
from apps.models import Uknow
from utils.constant import Status

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from apps.models import Uknow, FluentHardware, IcemHardware  # noqa
from dbs.database import TORTOISE_ORM
from config import configs


async def task_widget(task_id):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    query = await Uknow.filter(task_id=task_id).first()
    icem_start, icem_end = query.icem_start, query.icem_end
    fluent_start, fluent_end = query.fluent_start, query.fluent_end
    icem_level, fluent_level = query.icem_hardware_level, query.fluent_hardware_level
    icem_query = await IcemHardware.filter(level=icem_level).first()
    fluent_query = await FluentHardware.filter(level=fluent_level).first()
    icem_price, fluent_price = icem_query.price, fluent_query.price
    icem_duration = (icem_end - icem_start).total_seconds()
    fluent_duration = (fluent_end - fluent_start).total_seconds()

    compute_price = icem_price * icem_duration / 3600.0 + fluent_price * fluent_duration / 3600.0
    storage_price = ((icem_duration + fluent_duration) / 3600.0) * 0.508 * 150 / 720
    file_size = os.path.getsize(os.path.join(configs.ARCHIVE_PATH, task_id, 'fluent_result.zip'))
    download_price = file_size * 0.8246 / (1024.0 * 1024.0 * 1024.0)
    print(compute_price)
    print(round(compute_price + storage_price + download_price, 2))


async def get_time():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    query = await Uknow.filter(task_id='15609146-b7cf-11ed-90e2-d6ddea9e93de').first()
    if not query.create_time:
        total_seconds = 0
    else:
        total_seconds = ((datetime.datetime.now() + datetime.timedelta(hours=-8)).replace(
            tzinfo=pytz.timezone('UTC')) - query.create_time).total_seconds()
    print(total_seconds)
    # 如果有fluent_end, 优先用这个值
    if query.fluent_end:
        total_seconds = (query.fluent_end - query.create_time).total_seconds()
    # 如果fluent任务是pending, 并且时间大于3600, 此时时间应该为3600
    elif query.fluent_status == Status.PENDING and total_seconds > 3600:
        total_seconds = 3600
    else:
        # 如果Icem任务失败, 需要用Icem的时间
        if query.icem_status == Status.FAIL:
            if query.create_time:
                total_seconds = (query.icem_end - query.create_time).total_seconds()
            else:
                total_seconds = 0
        elif query.icem_status == Status.PENDING and total_seconds > 3600:
            total_seconds = 3600
        else:
            if query.create_time:
                total_seconds = ((datetime.datetime.now() + datetime.timedelta(hours=-8)).replace(
                    tzinfo=pytz.timezone('UTC')) - query.create_time).total_seconds()
            else:
                total_seconds = 0
    m, s = divmod(total_seconds, 60)
    print(f'{int(m)}分{int(s)}秒')


if __name__ == "__main__":
    run_async(get_time())
