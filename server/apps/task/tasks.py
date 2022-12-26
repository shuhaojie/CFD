"""
和UKnow进行交互的核心代码:
本脚本会一直对receive路径下的文件进行不间断扫描, 有文件过来时会对文件进行判断，如果文件通过验证, 会将文件移入到release下
"""

import os
import ast
import time
import pytz
import shutil
from tortoise import Tortoise
from tortoise.functions import Max
from datetime import datetime, timedelta

from config import configs
from apps.models import Uknow, IcemTask, Token, FluentTask, FluentProf, Archive
from dbs.database import TORTOISE_ORM
from utils.constant import Status
from apps.task.utils import FileTool, get_token, download_file, upload_file, create_job, create_remote_folder, \
    reverse_job, download_complete, task_fail
from logs import api_log
from utils.oss import Minio

minio = Minio()


async def monitor_task(task_id):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await Uknow.filter(task_id=task_id).update(
        create_time=datetime.now()
    )
    start_time = time.time()
    api_log.info(f'================Task {task_id} starts===================')
    print(f'================Task {task_id} starts===================')
    monitor_path, prepare_path, archive_path = r"{}".format(configs.MONITOR_PATH), r"{}".format(
        configs.PREPARE_PATH), r"{}".format(configs.ARCHIVE_PATH)
    stl_file_path = os.path.join(monitor_path, task_id + '.stl')
    minio_url = f'{configs.MINIO_END}:{configs.MINIO_PORT}:minio/{configs.MINIO_BUCKET}/{task_id}/'
    try:
        # 等待文件写入稳定
        FileTool.write_complete(stl_file_path)
        # md5校验
        query = await Uknow.filter(task_id=task_id).first()
        md5 = query.md5
        current_hash = FileTool.get_md5(stl_file_path)
        if md5 == current_hash:
            uknow_data_status = 'success'
        else:
            uknow_data_status = 'fail'

        # 校验成功
        if uknow_data_status == 'success':
            # 更新Uknow中的data_status
            await Uknow.filter(task_id=task_id).update(data_status=uknow_data_status)
            # 新建Icem文件夹
            icem_dst_path = os.path.join(prepare_path, task_id, 'icem')
            FileTool.make_directory(icem_dst_path)
            # 将数据移动到prepare路径下, 并重命名, task_id.stl -> vessel.stl
            shutil.move(stl_file_path, os.path.join(icem_dst_path, 'vessel.stl'))
            shutil.copy('./static/bash/mesh_auto.tcl', icem_dst_path)
            # 压缩Icem文件夹
            icem_zip_file = f'{icem_dst_path}.zip'
            FileTool.make_zipfile(icem_zip_file, icem_dst_path)
            # 计算Icem zip包的md5值
            icem_hash = FileTool.get_md5(icem_zip_file)
            print(icem_hash)
            await IcemTask.create(task_id=task_id, icem_md5=icem_hash)

            # 对并发数进行判断
            query = await IcemTask.filter()
            # 如果并发数小于10
            if len(query) < 10:
                # 更新task的状态
                await IcemTask.filter(task_id=task_id).update(task_status=Status.PENDING)
                icem_start = datetime.now()
                await Uknow.filter(task_id=task_id).update(
                    icem_status=Status.PENDING,
                    icem_start=icem_start
                )
                # 判斷token是否存在
                query = await Token.filter().first()
                if query:
                    # 如果存在, 先判斷token是否過期
                    expire_time = query.expire_time
                    now = datetime.now().replace(tzinfo=pytz.timezone('UTC'))
                    # 如果沒有過期，從數據庫中取token
                    if expire_time > now:
                        token = query.access_token
                    # 如果過期，需要重新獲取一次token
                    else:
                        token = get_token()
                        # 獲得完token之後，更新一下數據庫
                        expire_time = datetime.now() + timedelta(hours=10)
                        await Token.filter().update(access_token=token, expire_time=expire_time)
                # token不存在，也需要获取一下token
                else:
                    token = get_token()
                    # 獲得完token之後，將token入庫
                    expire_time = datetime.now() + timedelta(hours=10)
                    await Token.create(access_token=token, expire_time=expire_time)
                headers = {'Authorization': f'Bearer {token}'}
                # 等待icem zip文件写入稳定
                FileTool.write_complete(icem_zip_file)
                # 在速石上新建以task_id为名称的文件夹
                create_remote_folder(task_id, headers)
                # 上传Icem数据
                upload_file(task_id, 'icem', headers)
                # 5) 再发申请硬件资源的请求
                r = create_job(task_id, 'icem', icem_hash, headers)
                job_id = r.json()['id']
                await IcemTask.filter(task_id=task_id).update(job_id=job_id)
                # 6) 对任务状态进行轮询
                # 2. 开始Fluent任务
                # (1) 任务成功，取回fluent.msh，并移动到prepare路径下
                icem_finish = False
                while not icem_finish:
                    state = reverse_job(job_id)
                    print(state)
                    if state == 'COMPLETE':
                        print(time.time() - start_time)
                        print('Icem finish!!!!')
                        icem_end = datetime.now()
                        await Uknow.filter(task_id=task_id).update(
                            icem_status=Status.SUCCESS,
                            icem_end=icem_end,
                            icem_duration=float((icem_end - icem_start).seconds),
                        )
                        url = f'{configs.BASE_URL}/fa/api/v0/download/jobs/job-{job_id}/output/output/fluent.msh'
                        fluent_dst_path = os.path.join(configs.PREPARE_PATH, task_id, 'fluent')
                        FileTool.make_directory(fluent_dst_path)
                        download_file(url, fluent_dst_path, headers)
                        # (2) 等待文件下载完全下载下来
                        fluent_msh_file = os.path.join(fluent_dst_path, 'fluent.msh')
                        download_complete(fluent_msh_file)
                        # (3) 将prof文件复制到文件夹中, 具体要根据用户的选择
                        query = await Uknow.filter(task_id=task_id).first()
                        fluent_params = query.fluent_params
                        fluent_prof = ast.literal_eval(fluent_params)['prof']
                        query = await FluentProf.filter(prof_name=fluent_prof).first()
                        prof_path = query.prof_path
                        # 移动prof文件并重命名
                        shutil.copy(f'./static/prof/{prof_path}',
                                    os.path.join(fluent_dst_path, 'ICA_from_ICA_fourier_mass.prof'))
                        # (4) 将jou文件复制到路径下
                        shutil.copy('./static/bash/cfd_auto.jou', fluent_dst_path)
                        # (4) 将fluent文件夹进行打包
                        output_filename = f'{fluent_dst_path}.zip'
                        FileTool.make_zipfile(output_filename, fluent_dst_path)

                        # (5) 计算fluent的md5
                        fluent_md5 = FileTool.get_md5(output_filename)
                        await FluentTask.create(task_id=task_id, fluent_md5=fluent_md5)
                        # (6) 上传文件到速石
                        upload_file(task_id, 'fluent', headers)
                        # (7) 创建fluent任务
                        r = create_job(task_id, 'fluent', fluent_md5, headers)
                        job_id = r.json()['id']
                        await FluentTask.filter(task_id=task_id).update(job_id=job_id)
                        fluent_start = datetime.now()
                        await Uknow.filter(task_id=task_id).update(
                            fluent_status=Status.PENDING,
                            fluent_start=fluent_start
                        )
                        # (8) 对任务状态进行轮询
                        fluent_finish = False
                        while not fluent_finish:
                            state = reverse_job(job_id)
                            print(state)
                            if state == 'COMPLETE':
                                url = f'{configs.BASE_URL}/fa/api/v0/download/jobs/job-{job_id}/output/output/fluent_result.zip'
                                file_path = os.path.join(configs.PREPARE_PATH, task_id)
                                download_file(url, file_path, headers)
                                # (9) 等待文件下载完全下载下来
                                fluent_result_zip = os.path.join(file_path, 'fluent_result.zip')
                                download_complete(fluent_result_zip)
                                # (10) 将文件结果上传到minio
                                minio.upload_file(f'{task_id}/fluent_result.zip', fluent_result_zip)
                                # (11) 更新Uknow, FluentTask表
                                fluent_end = datetime.now()

                                await Uknow.filter(task_id=task_id).update(
                                    fluent_status=Status.SUCCESS,
                                    fluent_end=fluent_end,
                                    fluent_duration=float((fluent_end - fluent_start).seconds),
                                    fluent_result_file_path=minio_url,
                                )
                                # (12) 将文件夹移动到archive下进行归档
                                archive_path = os.path.join(configs.ARCHIVE_PATH, task_id)
                                if os.path.isdir(archive_path):
                                    shutil.rmtree(archive_path)
                                shutil.move(file_path, configs.ARCHIVE_PATH)
                                icem_finish = True
                                fluent_finish = True
                            elif state == 'FAILED':
                                task_fail(task_id, job_id, headers)
                                # 更新状态
                                await Uknow.filter(task_id=task_id).update(
                                    fluent_status=Status.FAIL,
                                    fluent_log_file_path=minio_url,
                                )
                                await FluentTask.filter(task_id=task_id).delete()
                                await Archive.create(
                                    task_id=task_id,
                                    task_type='fluent',
                                    task_status=Status.FAIL
                                )
                                icem_finish = True
                                fluent_finish = True
                            else:
                                time.sleep(5)
                    elif state == 'FAILED':
                        task_fail(task_id, job_id, headers)
                        # 更新状态
                        await Uknow.filter(task_id=task_id).update(
                            icem_status=Status.FAIL,
                            icem_log_file_path=minio_url,
                        )
                        await IcemTask.filter(task_id=task_id).delete()
                        await Archive.create(
                            task_id=task_id,
                            task_type='icem',
                            task_status=Status.FAIL
                        )
                        # 结束循环
                        icem_finish = True
                    else:
                        time.sleep(5)
            # 如果并发数大于10, 需要排队
            else:
                max_queue_number = await IcemTask.all().annotate(data=Max('await_number')).first()
                await IcemTask.filter(task_id=task_id).update(await_number=max_queue_number.await_number + 1)
        # 2) 校验不通过:
        else:
            # (1) 数据移动到失败的路径下
            shutil.move(stl_file_path, archive_path)
            # (2) 更新数据记录
            await Uknow.filter(task_id=task_id).update(
                data_status=Status.FAIL,
                data_code='数据不完整')
    except Exception as e:
        await IcemTask.filter(task_id=task_id).delete()  # 如果前面某一步除了問題，需要及時將數據記錄刪掉
        import traceback
        f = traceback.format_exc()
        print(f)
        api_log.error(e)
