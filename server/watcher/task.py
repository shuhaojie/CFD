import hashlib
import os
import time
import shutil

from config import configs
from logs import api_log
from apps.models import Task, Uknow, TaskQueue


def watcher_init():
    monitor_path = r"{}".format(configs.MONITOR_PATH)
    archive_path = r"{}".format(configs.ARCHIVE_PATH)
    folder_list = os.listdir(monitor_path)
    if len(folder_list) == 0:
        api_log.info(f"No files in {monitor_path} currently.")
    else:
        for f in folder_list:

            # 1. 首先对文件进行md5校验
            task_id, abs_path = f.split('.')[0], os.path.join(monitor_path, f)
            uknow_data_status = check_md5(task_id, abs_path)
            Uknow.filter(task_id=task_id).update(status=uknow_data_status)

            # 2. 根据状态做不同的处理

            # 1) 数据完整: 将数据移动到速石路径下
            # a. 如果任务数小于阈值, Task数据库插入一条记录
            # b. 如果任务数大于阈值, TaskQueue插入一条记录
            if uknow_data_status == 'success':
                shutil.move(abs_path, archive_path)
                query = await Task.filter(status='pending')
                if len(query) < 10:
                    Task.create(
                        task_id=task_id,
                    )
                else:
                    query = await TaskQueue.filter()
                    TaskQueue.create(
                        task_id=task_id,
                        queue_number=len(query)+1
                    )
            # 2) 数据不完整: 数据移动到失败的路径下
            elif uknow_data_status == 'fail':
                pass
            # 3) 数据还没传完, 等待即可
            else:
                pass


def check_md5(file_path, task_id):
    diff_time = time.time() - os.stat(file_path).st_mtime
    if diff_time < configs.FILE_DIFF_TIME:  # 如果文件修改时间比阈值小, 说明文件还没有稳定
        return 'pending'
    else:
        query = await Uknow.filter(task_id=task_id).first()
        md5 = query.md5
        with open(file_path, "rb") as f:
            current_bytes = f.read()
            current_hash = hashlib.md5(current_bytes).hexdigest()
        if md5 == current_hash:
            return 'success'
        else:
            return 'fail'
