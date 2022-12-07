from pydantic import BaseModel, Field
from typing import Optional, List
from copy import copy
from fastapi import Query
from tortoise.contrib.pydantic import pydantic_queryset_creator

from commons.schemas import BaseResponse
from apps.models import Task


class StartResponseSchema(BaseResponse):
    task_id: Optional[str] = Field('', title="task_id")


class SendDataRequestSchema(BaseModel):
    task_id: str
    md5: str
    username: Optional[str] = Field(title="用户名")
    hardware: str


class ReverseDataRequestSchema(BaseModel):
    task_id: str
    md5: str
    username: Optional[str] = Field(title="密码")
    hardware: str


class TaskListRequest:
    @property
    def response(self):
        return {'status': True, 'message': '', 'data': None, 'code': 200}

    @staticmethod
    def param(task_id_list: List[str] = Query([], title="task_id列表"), ):
        query_data = {"uuid_list": task_id_list}
        return query_data

    async def get(self, uuid_list: List[str]):
        response = copy(self.response)
        pqc = pydantic_queryset_creator(Task)
        if isinstance(uuid_list, list) and len(uuid_list) == 0:
            query_set = Task.filter()
        else:
            query_set = Task.filter(uuid__in=uuid_list)
        query_data = await pqc.from_queryset(query_set)
        response["data"] = query_data.dict()['__root__']
        response['message'] = '查询成功'
        return response
