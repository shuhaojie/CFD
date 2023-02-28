"""
和UKnow进行交互的核心代码:
本脚本会一直对receive路径下的文件进行不间断扫描, 有文件过来时会对文件进行判断，如果文件通过验证, 会将文件移入到release下
"""
import os
import time
import asyncio
import shutil
from tortoise import Tortoise
from dateutil.parser import parse
from datetime import datetime, timedelta

from config import configs
from apps.models import Uknow, FluentProf
from dbs.database import TORTOISE_ORM
from utils.constant import Status
from apps.task.utils import FileTool, get_token, download_file, upload_file, create_job, create_remote_folder, \
    reverse_job, download_complete, task_fail, task_widget, send_mail
from logs import api_log
from utils.oss import Minio

minio = Minio()
monitor_path, prepare_path = r"{}".format(configs.MONITOR_PATH), r"{}".format(configs.PREPARE_PATH)


async def monitor_task(task_id, md5, username, mac_address, icem_hardware_level, fluent_hardware_level,
                       prof, order_id):
    print(f'================Task {task_id} starts===================')
    api_log.info(f'================Task {task_id} starts===================')
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        zip_file_path = os.path.join(monitor_path, task_id + '.zip')
        minio_base_url = f'http://{configs.MINIO_END}:{configs.MINIO_PORT}/{configs.MINIO_BUCKET}/{task_id}'
        result_file = 'fluent_result.zip'
        # 首先将开始时间做更新
        await Uknow.create(
            task_id=task_id,
            md5=md5,
            username=username,
            mac_address=mac_address,
            icem_hardware_level=icem_hardware_level,
            fluent_hardware_level=fluent_hardware_level,
            fluent_prof=prof,
            icem_status=Status.PENDING,
            data_status=Status.SUCCESS,
            order_id=order_id,
        )
        uknow_query = await Uknow.filter(task_id=task_id).first()

        # 等待文件写入稳定
        FileTool.write_complete(zip_file_path)

        # 新建Icem文件夹
        icem_dst_path = os.path.join(prepare_path, task_id, 'icem')
        FileTool.make_directory(icem_dst_path)

        # 将软件传过来的zip包进行解压
        zip_to = os.path.join(monitor_path, task_id)
        FileTool.unzip_file(zip_file_path, zip_to)

        # 将vessel.stl数据移动到prepare/icem路径下
        shutil.move(os.path.join(zip_to, 'vessel.stl'), icem_dst_path)
        # 将mesh_auto.usf数据移动到prepare/icem路径下
        shutil.move(os.path.join(zip_to, 'mesh_auto.usf'), icem_dst_path)

        # 压缩Icem文件夹
        icem_zip_file = f'{icem_dst_path}.zip'
        FileTool.make_zipfile(icem_zip_file, icem_dst_path)

        # 计算Icem zip包的md5值, 创建任务的时候需要交给速石做文件完整性校验
        icem_hash = FileTool.get_md5(icem_zip_file)

        # 获取token
        token = await get_token()
        headers = {'Authorization': f'Bearer {token}'}

        # 等待icem zip文件写入稳定
        FileTool.write_complete(icem_zip_file)

        # 在速石上新建以task_id为名称的文件夹
        create_remote_folder(task_id, headers)

        # 上传Icem数据
        upload_file(task_id, 'icem', headers)

        # 发送申请硬件资源的请求并拿到速石返回的job_id
        r = create_job(task_id, 'icem', icem_hash, headers, uknow_query.icem_hardware_level)
        job_id = r.json()['id']

        # 对任务状态进行轮询
        icem_finish = False
        while not icem_finish:
            # 获取任务状态
            res = reverse_job(job_id, headers)
            state = res['state']
            api_log.info(f'Icem job {job_id} state:{state}')
            print(f'Icem job {job_id} state:{state}')
            if state == 'COMPLETE':
                api_log.info(f'Icem job {job_id} finish!!!!')
                print(f'Icem job {job_id} finish!!!!')
                # 采用速石传回来的 任务开始/任务结束 时间, 方便后续计算费用
                icem_start, icem_end = parse(res['createdAt']) + timedelta(hours=8), parse(
                    res['finishedAt']) + timedelta(hours=8)
                await Uknow.filter(task_id=task_id).update(
                    icem_status=Status.SUCCESS,
                    icem_start=icem_start,  # 用速石返回的时间, 计算的费用才是准确的
                    icem_end=icem_end,
                    icem_duration=float((icem_end - icem_start).seconds),
                )
                url = f'{configs.SUSHI_URL}/fa/api/v0/download/jobs/job-{job_id}/output/output/fluent.msh'
                fluent_dst_path = os.path.join(configs.PREPARE_PATH, task_id, 'fluent')
                FileTool.make_directory(fluent_dst_path)
                # 下载fluent.msh文件
                download_file(url, fluent_dst_path, headers)
                # 等待文件下载完全下载下来
                fluent_msh_file = os.path.join(fluent_dst_path, 'fluent.msh')
                download_complete(fluent_msh_file)
                # 将prof文件复制到文件夹中, 具体要根据用户的选择
                fluent_prof_query = await FluentProf.filter(prof_name=uknow_query.fluent_prof).first()
                prof_path = fluent_prof_query.prof_path
                # 移动prof文件并重命名, 这里统一重命名为ICA(因为脚本中是ICA)
                shutil.copy(f'./static/prof/{prof_path}', fluent_dst_path)
                # 将jou文件复制到路径下
                shutil.move(os.path.join(zip_to, 'cfd_auto.usf'), fluent_dst_path)
                # 将fluent文件夹进行打包
                output_filename = f'{fluent_dst_path}.zip'
                FileTool.make_zipfile(output_filename, fluent_dst_path)

                # 计算fluent的md5
                fluent_md5 = FileTool.get_md5(output_filename)
                # 上传文件到速石
                upload_file(task_id, 'fluent', headers)
                # 创建fluent任务
                r = create_job(task_id, 'fluent', fluent_md5, headers, uknow_query.fluent_hardware_level)
                job_id = r.json()['id']
                fluent_start = datetime.now()
                await Uknow.filter(task_id=task_id).update(
                    fluent_status=Status.PENDING,
                    fluent_start=fluent_start
                )
                # 对任务状态进行轮询
                fluent_finish = False
                while not fluent_finish:
                    res = reverse_job(job_id, headers)
                    state = res['state']
                    api_log.info(f'Fluent job {job_id} state:{state}')
                    print(f'Fluent job {job_id} state:{state}')
                    if state == 'COMPLETE':
                        api_log.info(f'Fluent job {job_id} finish!!!!')
                        print(f'Fluent job {job_id} finish!!!!')
                        url = f'{configs.SUSHI_URL}/fa/api/v0/download/jobs/job-{job_id}/output/output/{result_file}'
                        file_path = os.path.join(configs.PREPARE_PATH, task_id)
                        download_file(url, file_path, headers)
                        # 等待文件下载完全下载下来
                        fluent_result_zip = os.path.join(file_path, result_file)
                        download_complete(fluent_result_zip)
                        # 将文件结果上传到minio
                        minio.upload_file(f'{task_id}/{result_file}', fluent_result_zip)
                        # 更新Uknow, FluentTask表
                        fluent_start, fluent_end = parse(res['createdAt']) + timedelta(hours=8), parse(
                            res['finishedAt']) + timedelta(hours=8)
                        # 先更新一下数据, 不然计算费用的时候查不出
                        await Uknow.filter(task_id=task_id).update(
                            fluent_status=Status.SUCCESS,
                            fluent_start=fluent_start,
                            fluent_end=fluent_end,
                            fluent_duration=float((fluent_end - fluent_start).seconds),
                            fluent_result_file_path=f'{minio_base_url}/{result_file}',
                        )
                        widget = await task_widget(task_id)
                        await Uknow.filter(task_id=task_id).update(
                            widgets=widget,
                        )
                        # 将文件夹移动到archive下进行归档
                        archive_path = os.path.join(configs.ARCHIVE_PATH, task_id)
                        if os.path.isdir(archive_path):
                            shutil.rmtree(archive_path)
                        shutil.move(file_path, configs.ARCHIVE_PATH)
                        # 发送邮件
                        try:
                            # 有可能会出现网络断开的问题
                            await send_mail(task_id)
                        except Exception as e:
                            print(e)
                            await send_mail(task_id, 'NETWORK')
                        icem_finish = True
                        fluent_finish = True
                    elif state == 'FAILED':
                        task_fail(task_id, job_id, headers)
                        # 更新状态
                        fluent_end = datetime.now()
                        await Uknow.filter(task_id=task_id).update(
                            fluent_status=Status.FAIL,
                            fluent_end=fluent_end,
                            fluent_log_file_path=f'{minio_base_url}/stderr.txt',
                        )
                        widget = await task_widget(task_id, task_status='FAIL')
                        await Uknow.filter(task_id=task_id).update(widgets=widget)
                        await send_mail(task_id, task_status='FAIL', job_id=job_id)
                        icem_finish = True
                        fluent_finish = True
                    else:
                        await asyncio.sleep(5)
            elif state == 'FAILED':
                task_fail(task_id, job_id, headers)
                # 更新状态
                icem_end = datetime.now()
                await Uknow.filter(task_id=task_id).update(
                    icem_status=Status.FAIL,
                    icem_end=icem_end,
                    icem_log_file_path=f'{minio_base_url}/stderr.txt',
                )
                widget = await task_widget(task_id, task_status='FAIL')
                await Uknow.filter(task_id=task_id).update(widgets=widget)
                # 结束循环
                await send_mail(task_id, task_status='FAIL', job_id=job_id)
                icem_finish = True
            else:
                # 如果任务既没有成功, 也没有失败, 那么就休眠5秒后再轮询
                await asyncio.sleep(5)
    except Exception as e:
        import traceback
        f = traceback.format_exc()
        print(f)
        api_log.error(e)
        await asyncio.sleep(5)
