import os
import uuid
from fastapi import Depends, File, UploadFile
from fastapi_restful.inferring_router import InferringRouter
from fastapi_restful.cbv import cbv

from commons.schemas import BaseResponse, get_serialize_pydantic
from apps.models import Task
from .schemas import StartResponseSchema, SendDataRequestSchema, TaskListRequest
from config import configs

uknow_router = InferringRouter(prefix="", tags=['UKnow'])

sushi_router = InferringRouter(prefix="", tags=['Sushi'])


@uknow_router.post("/fetch_task_id", name="获取task_id", response_model=StartResponseSchema)
async def fetch_task_id():
    task_id = str(uuid.uuid1())
    return {'code': 200, "message": "获取task_id成功", 'status': True, "task_id": task_id}


@uknow_router.post("/send_configs", name="发送配置", response_model=BaseResponse)
async def send_configs(query_data: SendDataRequestSchema):
    md5 = query_data.md5
    task_id = query_data.task_id
    hardware = query_data.hardware
    await Task.create(
        task_id=task_id,
        md5=md5,
        hardware=hardware,
    )
    return {'code': 200, "message": "", 'status': True}


# https://stackoverflow.com/a/70657621/10844937
@uknow_router.post("/upload_file", name="发送数据文件", response_model=BaseResponse)
async def upload(file: UploadFile):
    try:
        contents = file.file.read()
        write_path = os.path.join(configs.MONITOR_PATH, file.filename)
        with open(write_path, 'wb') as f:
            f.write(contents)
    except Exception as e:
        return {"message": f"There was an error {e} uploading the file"}
    finally:
        file.file.close()
    return {'code': 200, "message": "", 'status': True}


@cbv(uknow_router)
class TaskListCBV:
    response_model = get_serialize_pydantic(Task)

    @uknow_router.get("/reverse_status", name="轮询任务状态", response_model=response_model)
    async def reverse_status(self, query_data: dict = Depends(TaskListRequest.param)):
        response = await TaskListRequest().get(**query_data)
        return response


@sushi_router.post("/login", name="demo")
async def login():
    return {'code': 200, "message": "api for demo", 'status': True, "token": "abc"}
