import os
import shutil
import uuid
import pytz
import datetime
from fastapi import UploadFile
from fastapi_restful.inferring_router import InferringRouter
from pydantic.typing import Literal
from typing import List
from fastapi import Query, BackgroundTasks
from dbs.database import TORTOISE_ORM, database_init
from tortoise import Tortoise
from apps.models import Uknow
from .utils import FileTool, get_user_info
from .schemas import UploadResponse
from worker import run_task
from config import configs
from utils.constant import Status

uknow_router = InferringRouter(prefix="", tags=['UKnow'])


# https://stackoverflow.com/a/70657621/10844937
@uknow_router.post("/upload", name="上传文件", response_model=UploadResponse)
async def upload(file: UploadFile,
                 md5: str,
                 mac_address: str,
                 order_id: str,
                 prof: Literal['ICA', 'ACA', 'BA', 'MCA', 'VA'],
                 icem_hardware_level: Literal['low', 'medium', 'high'],
                 fluent_hardware_level: Literal['low', 'medium', 'high'],
                 background_tasks: BackgroundTasks,
                 ):
    # 1. 先写入文件
    try:
        contents = file.file.read()
        write_path = os.path.join(configs.MONITOR_PATH, file.filename)
        with open(write_path, 'wb') as f:
            f.write(contents)
    except Exception as e:
        print(e)
        return {'code': 200, "message": f"{e}", 'status': False}
    finally:
        file.file.close()

    # 2. md5校验
    file_md5 = FileTool.get_md5(write_path)
    if file_md5 != md5:
        return {'code': 200, "message": "md5校验未通过, 请检查数据", "task_id": None, "status": False}
    # 3. 检查文件是否是zip文件
    if not file.filename.endswith('zip'):
        return {'code': 200, "message": "请上传zip文件", "task_id": None, "status": False}
    task_id = str(uuid.uuid1())
    # 6. 数据入库
    res = get_user_info(order_id)
    if not res['status']:
        return {'code': 200, "message": res['message'], 'task_id': None, 'status': False}
    username = res['data']['username']
    standard_file = os.path.join(configs.MONITOR_PATH, task_id + '.zip')
    shutil.move(write_path, standard_file)
    background_tasks.add_task(run_task, task_id, md5, username, mac_address, icem_hardware_level, fluent_hardware_level,
                              prof, order_id)
    return {'code': 200, "message": "文件上传成功, 任务即将开始", 'task_id': task_id, 'status': True}


@uknow_router.get("/get_status", name="状态查询")
async def get_status(task_id_list: List[str] = Query([], title="task_id列表")):
    await database_init()
    all_task_id_list = await Uknow.all().values_list("task_id", flat=True)
    await Tortoise.close_connections()
    if len(task_id_list) == 0:
        return {'code': 200, "message": "请输入task_id", 'status': False}
    elif not set(task_id_list).issubset(set(all_task_id_list)):
        return {'code': 200, "message": "存在不合法task_id, 请检查", 'status': False}
    else:
        item_list = []
        for task_id in task_id_list:
            item_dict = {}
            await database_init()
            query = await Uknow.filter(task_id=task_id).first()
            await Tortoise.close_connections()
            item_dict['任务id'] = task_id
            item_dict['任务名称'] = query.task_name if query.task_name else '-'
            item_dict['用户名'] = query.username if query.username else '-'
            item_dict['创建时间'] = query.create_time.strftime("%Y-%m-%d %H:%M:%S") if query.create_time else '-'

            # 任务状态
            if not query.icem_status:
                item_dict['任务状态'] = '数据上传成功'
            else:
                if query.icem_status == Status.PENDING:
                    item_dict['任务状态'] = 'Icem处理中'
                elif query.icem_status == Status.FAIL:
                    item_dict['任务状态'] = 'Icem处理失败'
                elif query.icem_status == Status.QUEUE:
                    queue_number = query.task_queue
                    item_dict['任务状态'] = f'任务排队中, 排队号{queue_number}'
                else:
                    if not query.fluent_status:
                        item_dict['任务状态'] = 'Icem处理成功'
                    else:
                        if query.fluent_status == Status.PENDING:
                            item_dict['任务状态'] = 'Fluent处理中'
                        elif query.fluent_status == Status.FAIL:
                            item_dict['任务状态'] = 'Fluent处理失败'
                        else:
                            item_dict['任务状态'] = '任务成功'

            # 任务耗时
            if query.fluent_end:
                total_seconds = (query.fluent_end - query.create_time).total_seconds()
            else:
                # 如果Icem任务失败, 需要用Icem的时间
                if query.icem_status == Status.FAIL:
                    total_seconds = (query.icem_end - query.create_time).total_seconds()
                else:
                    if query.create_time:
                        total_seconds = ((datetime.datetime.now() + datetime.timedelta(hours=-8)).replace(
                            tzinfo=pytz.timezone('UTC')) - query.create_time).total_seconds()
                    else:
                        total_seconds = 0
            m, s = divmod(total_seconds, 60)
            item_dict['任务耗时'] = f'{int(m)}分{int(s)}秒'

            # 任务花费
            if query.widgets:
                item_dict['任务花费'] = f'{query.widgets}元'
            else:
                item_dict['任务花费'] = '-'

            # 日志/结果文件
            if query.fluent_result_file_path:
                item_dict['结果/日志文件'] = query.fluent_result_file_path
            if query.icem_log_file_path:
                item_dict['结果/日志文件'] = query.icem_log_file_path
            if query.fluent_log_file_path:
                item_dict['结果/日志文件'] = query.fluent_log_file_path
            item_list.append(item_dict)
    return {'code': 200, "data": item_list, "message": "状态获取成功", 'status': True}
