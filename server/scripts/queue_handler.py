import os
import sys
import time
from tortoise import Tortoise, run_async
from tortoise.expressions import Q

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from dbs.database import TORTOISE_ORM
from apps.models import Uknow, IcemTask
from worker import run_task


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    # task_queue非空列表
    while True:
        query_list = await Uknow.filter(~Q(task_queue=None))
        if len(query_list) == 0:
            time.sleep(60)  # 没有排队的就休眠1分钟
        else:
            total_icem_task = len(await IcemTask.all())
            if total_icem_task > 10:
                time.sleep(10)  # Icem任务数如果超过阈值, 休眠10秒
            else:
                for query in query_list:
                    if query.task_queue >= 2:
                        # 排队号大于等于2的, 往前排一个
                        await Uknow.filter(uuid=query.uuid).update(task_queue=query.task_queue - 1)
                    else:  # 排队号等于1, 发任务
                        run_task.apply_async((query.task_id,))


if __name__ == "__main__":
    run_async(run())
