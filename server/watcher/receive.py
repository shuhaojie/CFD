"""
和UKnow进行交互的核心代码:
本脚本会一直对receive路径下的文件进行不间断扫描, 有文件过来时会对文件进行判断，如果文件通过验证, 会将文件移入到release下
"""

import hashlib
import os
import sys
import time
import shutil
import zipfile
from tortoise import Tortoise, run_async
from tortoise.functions import Max
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config import configs  # noqa
from apps.models import Uknow, IcemTask, Token
from dbs.database import TORTOISE_ORM  # noqa
from .utils import get_token


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    monitor_path, prepare_path, archive_path = r"{}".format(configs.MONITOR_PATH), r"{}".format(
        configs.PREPARE_PATH), r"{}".format(configs.ARCHIVE_PATH)
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

            # 2. 根据状态做不同的处理
            # 1) 校验:
            # a. 更新data_status
            # b. 将数据移动到prepare路径下
            # c. 将zip包进行解压
            # d. 压缩Icem文件夹
            # e. 计算icem的md5值
            # f. IcemTask新增一条记录, 入库task_id和md5
            if uknow_data_status == 'success':
                await Uknow.filter(task_id=task_id).update(status=uknow_data_status)
                shutil.move(abs_path, prepare_path)

                path_to_zip_file = os.path.join(prepare_path, f)
                directory_to_extract_to = path_to_zip_file.split('.')[0]
                with zipfile.ZipFile(abs_path, 'r') as zip_ref:
                    zip_ref.extractall(directory_to_extract_to)

                dir_name = os.path.join(directory_to_extract_to, 'icem')
                output_filename = f'{dir_name}.zip'
                shutil.make_archive(output_filename, 'zip', dir_name)

                with open(dir_name, "rb") as f1:
                    current_bytes = f1.read()
                    a_hash = hashlib.md5(current_bytes).hexdigest()
                await IcemTask.create(task_id=task_id, icem_md5=a_hash)
            # 2) 校验不通过:
            # a. 数据移动到失败的路径下
            # b. 删掉Release中的数据记录
            elif uknow_data_status == 'fail':
                shutil.move(abs_path, archive_path)
                await Uknow.filter(task_id=task_id).update(data_status='fail', status_code='数据不完整')
            # 3) 数据还没传完, 等待传完即可
            else:
                pass

            # 1. 对并发数进行判断
            query = await IcemTask.filter()
            # 如果并发数小于10
            if len(query) < 10:
                token = get_token()
                await Token.update_or_create(access_token=token)
            else:
                max_queue_number = await IcemTask.all().annotate(data=Max('await_number')).first()
                await IcemTask.filter(task_id=task_id).update(await_number=max_queue_number.await_number+1)


if __name__ == "__main__":
    run_async(run())
