import uuid
from fastapi import Depends
from fastapi_restful.inferring_router import InferringRouter
from fastapi_restful.cbv import cbv

from commons.schemas import BaseResponse, get_serialize_pydantic
from apps.models import Task
from .schemas import StartResponseSchema, SendDataRequestSchema, TaskListRequest


router = InferringRouter(prefix="", tags=['UKnow'])


@router.get("/get_task_id", name="获取task_id", response_model=StartResponseSchema)
async def get_task_id():
    task_id = str(uuid.uuid1())
    return {'code': 200, "message": "获取task_id成功", 'status': True, "task_id": task_id}


@router.post("/send_data", name="发送数据", response_model=BaseResponse)
async def send_data(query_data: SendDataRequestSchema):
    md5 = query_data.md5
    task_id = query_data.task_id
    hardware = query_data.hardware
    await Task.create(
        task_id=task_id,
        md5=md5,
        hardware=hardware,
    )
    return {'code': 200, "message": "", 'status': True}


@cbv(router)
class TaskListCBV:
    response_model = get_serialize_pydantic(Task)

    @router.get("/reverse_data", name="轮询任务状态", response_model=response_model)
    async def reverse_data(self, query_data: dict = Depends(TaskListRequest.param)):
        response = await TaskListRequest().get(**query_data)
        return response
