import os
import shutil
import pytz
import datetime
from fastapi import UploadFile
from fastapi_restful.inferring_router import InferringRouter
from pydantic.typing import Literal
from typing import List
from fastapi import Query
from tortoise.models import Q
from apps.models import Uknow
from .utils import FileTool, get_user_info
from .schemas import UploadResponse
from worker import run_task
from celery_utils import get_celery_worker, get_all_worker
from config import configs
from utils.constant import Status
from logs import api_log

uknow_router = InferringRouter(prefix="", tags=['UKnow'])


def printus(result):
    print(result)  # task id
    print(result.ready())  # returns True if the task has finished processing.
    print(result.result)  # task is not ready, so no return value yet.
    print(result.get())  # Waits until the task is done and returns the retval.
    print(result.result)  # direct access to result, doesn't re-raise errors.
    print(result.successful())  # returns True if the task didn't end in failure.)


# https://stackoverflow.com/a/70657621/10844937
@uknow_router.post("/upload", name="上传文件", response_model=UploadResponse)
async def upload(file: UploadFile,
                 md5: str,
                 mac_address: str,
                 order_id: str,
                 prof: Literal['ICA', 'ACA', 'BA', 'MCA', 'VA'],
                 icem_hardware_level: Literal['low', 'medium', 'high'],
                 fluent_hardware_level: Literal['low', 'medium', 'high'],
                 username: str | None = None,
                 task_name: str | None = None,
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
    # 4. 判断order_id是否正在跑或者排队
    query = await Uknow.filter(
        Q(order_id=order_id, icem_status=Status.QUEUE) | Q(order_id=order_id, icem_status=Status.PENDING) | Q(
            order_id=order_id, fluent_status=Status.QUEUE) | Q(order_id=order_id, fluent_status=Status.PENDING)).first()
    if query:
        return {'code': 200, "message": "该订单id正在处理中", "task_id": None, "status": False}
    # 5. 生成task_id
    now_time = datetime.datetime.now()
    query = await Uknow.filter(create_time__year=now_time.year,
                               create_time__month=now_time.month,
                               create_time__day=now_time.day,
                               create_time__hour=now_time.hour,
                               create_time__minute=now_time.minute,
                               create_time__second=now_time.second)
    index = len(query) + 1
    index = f'0{str(index)}' if index < 10 else f'{str(index)}'
    month = f'0{str(now_time.month)}' if now_time.month < 10 else f'{str(now_time.month)}'
    day = f'0{str(now_time.day)}' if now_time.day < 10 else f'{str(now_time.day)}'
    hour = f'0{str(now_time.hour)}' if now_time.hour < 10 else f'{str(now_time.hour)}'
    minute = f'0{str(now_time.minute)}' if now_time.minute < 10 else f'{str(now_time.minute)}'
    second = f'0{str(now_time.second)}' if now_time.second < 10 else f'{str(now_time.second)}'
    task_id = f'{now_time.year}{month}{day}{hour}{minute}{second}0{index}'
    # 6. 数据入库
    res = get_user_info(order_id)
    if not res['status']:
        return {'code': 200, "message": res['message'], 'task_id': None, 'status': False}
    username = res['data']['username']
    try:
        await Uknow.create(
            task_id=task_id,
            md5=md5,
            username=username,
            mac_address=mac_address,
            task_name=task_name,
            icem_hardware_level=icem_hardware_level,
            fluent_hardware_level=fluent_hardware_level,
            fluent_prof=prof,
            data_status=Status.SUCCESS,
            order_id=order_id,
        )
    except Exception as e:
        print(e)
        return {'code': 200, "message": "CFD后台数据库连接中断", 'task_id': None, 'status': False}
    # 7. 对文件重命名
    standard_file = os.path.join(configs.MONITOR_PATH, task_id + '.zip')
    shutil.move(write_path, standard_file)
    # 8. 发送异步任务
    # total_tasks = get_celery_worker()
    # print(f'Total Task:{total_tasks}')
    # 无论worker数有没有超过10个, 都需要将任务发布出去
    result = run_task.apply_async(args=(task_id,), expires=6000)
    printus(result)
    # if total_tasks < 10:
    await Uknow.filter(task_id=task_id).update(icem_status=Status.PENDING)
    return {'code': 200, "message": "文件上传成功, 任务即将开始", 'task_id': task_id, 'status': True}
    # else:
    #     await Uknow.filter(task_id=task_id).update(icem_status=Status.QUEUE)
    #     return {'code': 200, "message": "文件上传成功, 任务排队中", 'task_id': task_id, 'status': True}


@uknow_router.get("/get_status", name="状态查询")
async def get_status(task_id_list: List[str] = Query([], title="task_id列表")):
    all_task_id_list = await Uknow.all().values_list("task_id", flat=True)
    if len(task_id_list) == 0:
        return {'code': 200, "message": "请输入task_id", 'status': False}
    elif not set(task_id_list).issubset(set(all_task_id_list)):
        return {'code': 200, "message": "存在不合法task_id, 请检查", 'status': False}
    else:
        item_list = []
        for task_id in task_id_list:
            item_dict = {}
            query = await Uknow.filter(task_id=task_id).first()
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
