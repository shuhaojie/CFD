"""
和UKnow进行交互的核心代码:
本脚本会一直对receive路径下的文件进行不间断扫描, 有文件过来时会对文件进行判断，如果文件通过验证, 会将文件移入到release下
"""

import os
import sys
import pytz
import shutil
from tortoise import Tortoise, run_async
from tortoise.functions import Max
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config import configs
from apps.models import Uknow, IcemTask, Token
from dbs.database import TORTOISE_ORM
from watcher.utils import FileTool, get_token
from logs import api_log


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
            # 1) 首先对文件进行md5校验
            task_id, abs_path = f.split('.')[0], os.path.join(monitor_path, f)
            try:
                # 2) 等待文件写入稳定
                FileTool.write_complete(abs_path)
                query = await Uknow.filter(task_id=task_id).first()
                md5 = query.md5
                current_hash = FileTool.get_md5(abs_path)
                if md5 == current_hash:
                    uknow_data_status = 'success'
                else:
                    uknow_data_status = 'fail'

                if uknow_data_status == 'success':
                    # 3) 更新data_status
                    await Uknow.filter(task_id=task_id).update(data_status=uknow_data_status)
                    # 4) 将数据移动到prepare路径下
                    shutil.move(abs_path, prepare_path)
                    # 5) 将zip包进行解压
                    path_to_zip_file = os.path.join(prepare_path, f)
                    FileTool.unzip_file(path_to_zip_file, prepare_path)
                    # 6) 压缩Icem文件夹
                    dir_name = os.path.join(prepare_path, task_id, 'icem')
                    output_filename = f'{dir_name}.zip'
                    FileTool.make_zipfile(output_filename, dir_name)
                    # 7) 计算icem的md5值
                    icem_hash = FileTool.get_md5(output_filename)
                    await IcemTask.create(task_id=task_id, icem_md5=icem_hash)

                    # 对并发数进行判断
                    query = await IcemTask.filter()
                    # 如果并发数小于10
                    if len(query) < 10:
                        await IcemTask.filter(task_id=task_id).update(task_status='pending')
                        token = get_token()
                        query = await Token.filter().first()
                        if query:
                            expire_time = query.expire_time

                            now = datetime.now().replace(tzinfo=pytz.timezone('UTC'))
                            if expire_time > now:
                                pass
                            else:
                                expire_time = datetime.now() + timedelta(hours=10)
                                await Token.filter().update(access_token=token, expire_time=expire_time)
                        else:
                            expire_time = datetime.now() + timedelta(hours=10)
                            await Token.create(access_token=token, expire_time=expire_time)
                    else:
                        max_queue_number = await IcemTask.all().annotate(data=Max('await_number')).first()
                        await IcemTask.filter(task_id=task_id).update(await_number=max_queue_number.await_number + 1)
                # 2) 校验不通过:
                else:
                    # (1) 数据移动到失败的路径下
                    shutil.move(abs_path, archive_path)
                    # (2) 更新数据记录
                    await Uknow.filter(task_id=task_id).update(data_status='fail', data_code='数据不完整')
            except Exception as e:
                await IcemTask.filter(task_id=task_id).delete()  # 如果前面某一步除了問題，需要及時將數據記錄刪掉
                import traceback
                f = traceback.format_exc()
                print(f)
                api_log.error(e)


if __name__ == "__main__":
    run_async(run())
