"""
和速石进行交互的核心代码:
本脚本会一直对release路径下的文件进行不间断扫描, 有文件过来时会对文件进行判断，如果文件执行完成, 会将文件移入到archive下
"""
import os
import shutil
import sys
import time
from tortoise import Tortoise, run_async

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config import configs
from utils.constant import TaskStatus
from apps.models import Uknow, IcemTask, FluentTask
from dbs.database import TORTOISE_ORM
from watcher.utils import download_file, upload_file, create_job, create_remote_folder, reverse_job, \
    download_complete, FileTool


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    query_sets = await Uknow.filter(status="pending")
    prepare_path = r"{}".format(configs.PREPARE_PATH)
    if len(query_sets) == 0:
        print(f"No files in {prepare_path} currently.")
    else:
        base_url = 'http://120.48.150.243'
        for query in query_sets:
            task_id = query.task_id
            abs_path = os.path.join(prepare_path, task_id + ".zip")
            # 1. 开始Icem任务
            # 1) 等待文件写入稳定
            FileTool.write_complete(abs_path)
            # 2) 在速石上新建以task_id为名称的文件夹
            create_remote_folder(task_id)
            # 3) 上传Icem数据
            upload_file(task_id, 'icem')
            # 注: 当前速石并不支持用api的形式先去对md5进行校验，需要后续版本，这部分代码暂时comment out
            # 4) 校验文件是否稳定
            query = await IcemTask.filter(task_id=task_id).first()
            icem_md5 = query.icem_md5
            # 5) 再发申请硬件资源的请求
            r = create_job(task_id, 'icem', icem_md5)
            job_id = r.json()['job_id']
            await IcemTask.filter(task_id=task_id).update(job_id=job_id)
            # 6) 对任务状态进行轮询
            state = reverse_job(job_id)
            # 2. 开始Fluent任务
            # (1) 任务成功，取回fluent.msh，并移动到prepare路径下
            if state == 'COMPLETE':
                url = f'{base_url}/fa/api/v0/download/jobs/job-{job_id}/output/output/fluent.msh'
                file_path = os.path.join(configs.PREPARE_PATH, task_id, 'fluent')
                download_file(url, file_path)
                # (2) 等待文件下载完全下载下来
                fluent_msh_file = os.path.join(file_path, 'fluent.msh')
                download_complete(fluent_msh_file)
                # (3) 将prof文件复制到文件夹中, 具体要根据用户的选择
                query = await Uknow.filter(task_id=task_id).first()
                fluent_params = query.fluent_params
                # todo: 需要从fluent_params中取出prof文件
                shutil.copy('./static/prof/VA_from_ICA_fourier_mass.prof', file_path)
                # (4) 将fluent文件夹进行打包
                dest = os.path.join(configs.PREPARE_PATH, task_id, 'fluent.zip')
                FileTool.zip_folder(file_path, dest)
                # (5) 计算fluent的md5
                fluent_md5 = FileTool.get_md5(dest)
                await FluentTask.create(task_id=task_id, md5=fluent_md5)
                # (6) 上传文件到速石
                upload_file(dest, 'fluent')
                # (7) 创建fluent任务
                r = create_job(task_id, 'fluent', fluent_md5)
                job_id = r.json()['job_id']
                await FluentTask.filter(task_id=task_id).update(job_id=job_id)
                # (8) 对任务状态进行轮询
                state = reverse_job(job_id)
                if state == 'COMPLETE':
                    url = f'{base_url}/fa/api/v0/download/jobs/job-{job_id}/output/output/fluent-result.zip'
                    file_path = os.path.join(configs.PREPARE_PATH, task_id)
                    download_file(url, file_path)
                    # (9) 等待文件下载完全下载下来
                    fluent_result_zip = os.path.join(file_path, 'fluent-result.zip')
                    download_complete(fluent_result_zip)
                    # (10) 将文件结果上传到minio
                    # (11) 更新Uknow, FluentTask表
                    await Uknow.filter(task_id=task_id).update(
                        fluent_status=TaskStatus.SUCCESS
                    )
                    # (12) 将文件夹移动到archive下进行归档
                    shutil.move(file_path, configs.ARCHIVE_PATH)
                elif state == 'FAILED':
                    url = f'{base_url}/fa/api/v0/download/jobs/job-{job_id}/log/stderr.txt'
                    file_path = os.path.join(configs.PREPARE_PATH, task_id)
                    download_file(url, file_path)
                    # 将文件夹移动到archive下进行归档
                    shutil.move(file_path, configs.ARCHIVE_PATH)
                else:
                    time.sleep(5)
            elif state == 'FAILED':
                base_url = f'http://120.48.150.243/fa/api/v0/download/jobs/job-{job_id}/log/stderr.txt'
                file_path = os.path.join(configs.PREPARE_PATH, task_id)
                download_file(base_url, file_path)
                # 将日志上传到minio
            else:
                time.sleep(5)


if __name__ == "__main__":
    run_async(run())
