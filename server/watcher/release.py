import os
import sys
import time
import requests
from tortoise import Tortoise, run_async

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config import configs  # noqa
from apps.models import Task, Uknow, Queue  # noqa
from dbs.database import TORTOISE_ORM  # noqa
from .utils import get_token  # noqa


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    query_sets = await Task.filter(status="pending")
    prepare_path = r"{}".format(configs.PREPARE_PATH)
    if len(query_sets) == 0:
        print(f"No files in {prepare_path} currently.")
    else:
        # 有文件就会要传文件, 先拿token
        token = get_token()
        for query in query_sets:
            # 1. 首先判断文件是否稳定
            task_id = query.task_id
            abs_path = os.path.join(prepare_path, task_id + ".zip")
            diff_time = time.time() - os.stat(abs_path).st_mtime
            if diff_time < float(configs.FILE_DIFF_TIME):  # 如果文件修改时间比阈值小, 说明文件还没有稳定
                pass
            else:
                # 2. 文件已经稳定, 就可以开始发请求了
                # 1) 再发申请硬件资源的请求

                # 2) 再发数据上传的请求
                base_url = 'http://127.0.0.1:8000/reverse_status'
                header = ''
                # https://stackoverflow.com/a/22567429/10844937
                requests.post(base_url, files=abs_path)
                # 3) 判断前面两个请求是否成功

                # 4) 成功后发执行脚本的请求
                pass


if __name__ == "__main__":
    run_async(run())
