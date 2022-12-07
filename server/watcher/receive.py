"""
和UKnow进行交互的核心代码
"""

import hashlib
import os
import sys
import time
import shutil
from tortoise import Tortoise, run_async

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config import configs  # noqa
from apps.models import Task, Uknow, Queue  # noqa
from dbs.database import TORTOISE_ORM  # noqa


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    monitor_path, prepare_path = r"{}".format(configs.MONITOR_PATH), r"{}".format(configs.PREPARE_PATH)
    file_list = os.listdir(monitor_path)
    if len(file_list) == 0:
        print(f"No files in {monitor_path} currently.")
    else:
        for f in file_list:
            # 1. 首先对文件进行md5校验
            task_id, abs_path = f.split('.')[0], os.path.join(monitor_path, f)
            diff_time = time.time() - os.stat(abs_path).st_mtime
            # todo: 这部分写成一个function
            if diff_time < float(configs.FILE_DIFF_TIME):  # 如果文件修改时间比阈值小, 说明文件还没有稳定
                uknow_data_status = 'pending'
            else:
                query = await Uknow.filter(task_id=task_id).first()
                md5 = query.md5
                with open(abs_path, "rb") as f1:
                    current_bytes = f1.read()
                    current_hash = hashlib.md5(current_bytes).hexdigest()
                if md5 == current_hash:
                    uknow_data_status = 'success'
                else:
                    uknow_data_status = 'fail'
            await Uknow.filter(task_id=task_id).update(status=uknow_data_status)

            # 2. 根据状态做不同的处理
            # 1) 数据完整: 将数据移动到prepare下，准备移动到速石
            # a. 如果任务数小于阈值, Task数据库插入一条记录
            # b. 如果任务数大于阈值, TaskQueue插入一条记录
            if uknow_data_status == 'success':
                shutil.move(abs_path, prepare_path)
                query = await Task.filter(status='pending')
                if len(query) < 2:
                    await Task.create(
                        task_id=task_id,
                    )
                else:
                    query = await Queue.filter()
                    await Queue.create(
                        task_id=task_id,
                        queue_number=len(query) + 1
                    )
            # 2) 数据不完整: 数据移动到失败的路径下
            elif uknow_data_status == 'fail':
                pass
            # 3) 数据还没传完, 等待传完即可
            else:
                pass


if __name__ == "__main__":
    run_async(run())
