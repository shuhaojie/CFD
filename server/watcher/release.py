"""
和速石进行交互的核心代码:
本脚本会一直对release路径下的文件进行不间断扫描, 有文件过来时会对文件进行判断，如果文件执行完成, 会将文件移入到archive下
"""
import os
import json
import sys
import time
import requests
from tortoise import Tortoise, run_async

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config import configs
from apps.models import Uknow, IcemTask
from dbs.database import TORTOISE_ORM
from watcher.utils import get_token, download_file


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    query_sets = await Uknow.filter(status="pending")
    prepare_path = r"{}".format(configs.PREPARE_PATH)
    if len(query_sets) == 0:
        print(f"No files in {prepare_path} currently.")
    else:
        # 有文件就会要传文件, 先拿token
        token = get_token()
        headers = {
            'Authorization': f'Bearer {token}'
        }
        for query in query_sets:
            # 1. 首先判断文件是否稳定
            task_id = query.task_id
            abs_path = os.path.join(prepare_path, task_id + ".zip")
            diff_time = time.time() - os.stat(abs_path).st_mtime
            if diff_time < float(configs.FILE_DIFF_TIME):  # 如果文件修改时间比阈值小, 说明文件还没有稳定
                pass
            else:
                # 2. 文件已经稳定, 就可以开始发请求了
                # 1) 上传数据
                base_url = "http://120.48.150.243/fa/api/v0/upload/"
                abs_path = os.path.join(configs.PREPARE_PATH, task_id + ".zip")
                files = {
                    'file': open(abs_path, 'rb'),
                    'key': (None, f'dir1/{task_id}.zip'),
                    'storage_id': (None, '-1'),
                }
                requests.post(
                    base_url,
                    files=files,
                    headers=headers
                )
                # 注: 当前速石并不支持用api的形式先去对md5进行校验，需要后续版本，这部分代码暂时comment out
                # 2) 校验文件是否稳定
                query = await IcemTask.filter(task_id=task_id).first()
                icem_md5 = query.icem_md5
                # file_complete = False
                # while not file_complete:
                #     base_url = "http://120.48.150.243/fa/api/v0/upload/"
                #     params = {'md5': icem_md5}
                #     r = requests.post(base_url, json=params, headers=headers)
                #     complete = r.json()['complete']
                #     if complete:
                #         file_complete = True
                #     else:
                #         time.sleep(30)

                # 3) 再发申请硬件资源的请求

                base_url = 'http://120.48.150.243/api/v1/jobs'
                # 目前暂时用这个固定配置, 这个是根据用户选择的配置来的
                f = open('./static/sushi/icem_b1.c1.32.json', encoding='UTF-8')
                json_data = json.load(f)
                json_data['inputs'][0]['value'] = f'/{task_id}_icem.zip'
                json_data['inputs'][1]['value'] = icem_md5
                json_data['name'] = task_id
                # https://stackoverflow.com/a/22567429/10844937
                r = requests.post(base_url, json=json_data, headers=headers)
                job_id = r.json()['job_id']
                await IcemTask.filter(task_id=task_id).update(job_id=job_id)

                # 4) 对任务状态进行轮询
                base_url = f'http://120.48.150.243/api/v1/jobs/{job_id}'
                r = requests.get(base_url, headers=headers)
                state = r.json()['state']
                # 任务成功，取回fluent.msh，并移动到prepare路径下
                if state == 'COMPLETE':
                    base_url = f'http://120.48.150.243/fa/api/v0/download/jobs/job-{job_id}/output/output/fluent.msh'
                    file_path = os.path.join(configs.PREPARE_PATH, task_id, 'fluent')
                    download_file(base_url, file_path)
                elif state == 'FAILED':
                    base_url = f'http://120.48.150.243/fa/api/v0/download/jobs/job-{job_id}/log/stderr.txt'
                    file_path = os.path.join(configs.PREPARE_PATH, task_id, 'fluent')
                    download_file(base_url, file_path)
                    # 将日志上传到minio
                else:
                    pass


if __name__ == "__main__":
    run_async(run())
