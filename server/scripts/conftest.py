import os
import sys

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


if __name__ == "__main__":
    from tortoise import Tortoise, run_async

    run_async(task_widget('20221228092527001'))
