import os
from datetime import datetime
from fastapi import UploadFile, BackgroundTasks
from fastapi_restful.inferring_router import InferringRouter
from typing import List
from fastapi import Query

from commons.schemas import BaseResponse
from apps.models import Uknow
from .schemas import StartResponseSchema, SendDataRequestSchema, TaskListRequest
from worker import run_task
from config import configs

uknow_router = InferringRouter(prefix="", tags=['UKnow'])

sushi_router = InferringRouter(prefix="", tags=['Sushi'])


@uknow_router.post("/fetch_task_id", name="获取task_id", response_model=StartResponseSchema)
async def fetch_task_id():
    now_time = datetime.now()
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
    return {'code': 200, "message": "获取task_id成功", 'status': True, "task_id": task_id}


@uknow_router.post("/send_configs", name="发送配置", response_model=BaseResponse)
async def send_configs(query_data: SendDataRequestSchema):
    data = query_data.dict()
    task_id = data.get("task_id", None)
    username = data.get("username", None)
    md5 = data.get("md5", None)
    mac_address = data.get("mac_address", None)
    task_name = data.get("task_name", None)
    icem_hardware_level = data.get("icem_hardware_level", None)
    fluent_hardware_level = data.get("fluent_hardware_level", None)
    icem_params = data.get("icem_params", None)
    fluent_params = data.get("fluent_params", None)
    # 查看当前的数据条数, 如果是条数少于10, is_await就会False, 否则要排队
    task_id_list = await Uknow.all().values_list("task_id", flat=True)
    if task_id in task_id_list:
        return {'code': 200, "message": "task_id已存在", 'status': False}
    else:
        await Uknow.create(
            task_id=task_id,
            md5=md5,
            username=username,
            mac_address=mac_address,
            task_name=task_name,
            icem_hardware_level=icem_hardware_level,
            fluent_hardware_level=fluent_hardware_level,
            icem_params=icem_params,
            fluent_params=fluent_params,
        )
        return {'code': 200, "message": "配置发送成功", 'status': True}


# https://stackoverflow.com/a/70657621/10844937
@uknow_router.post("/upload_file", name="上传文件", response_model=BaseResponse)
async def upload(file: UploadFile, background_tasks: BackgroundTasks):
    try:
        contents = file.file.read()
        write_path = os.path.join(configs.MONITOR_PATH, file.filename)
        with open(write_path, 'wb') as f:
            f.write(contents)
    except Exception as e:
        return {"message": f"There was an error {e} uploading the file"}
    finally:
        file.file.close()
    task_id = file.filename.split('.')[0]
    task_id_list = await Uknow.all().values_list("task_id", flat=True)
    if task_id not in task_id_list:
        return {'code': 200, "message": "stl文件名错误", 'status': False}
    else:
        run_task.apply_async((task_id,))
        return {'code': 200, "message": "文件上传成功", 'status': True}


@uknow_router.get("/reverse_status", name="轮询任务状态")
async def reverse_status(task_id_list: List[str] = Query([], title="task_id列表")):
    if len(task_id_list) == 0:
        return {'code': 200, "message": "请输入task_id", 'status': True}
    else:
        item_list = []
        for task_id in task_id_list:
            item_dict = {}
            query = await Uknow.filter(task_id=task_id).first()
            item_dict['task_id'] = task_id
            item_dict['task_name'] = query.task_name
            item_list.append(item_dict)
    return {'code': 200, "data": item_list, "message": "状态获取成功", 'status': True}
