from pydantic import BaseModel, Field
from pydantic.typing import Literal
from typing import Optional, List, Dict
from copy import copy
from fastapi import Query
from tortoise.contrib.pydantic import pydantic_queryset_creator

from commons.schemas import BaseResponse
from apps.models import Uknow


class StartResponseSchema(BaseResponse):
    task_id: Optional[str] = Field('', title="task_id")


# https://stackoverflow.com/a/61248551/10844937
class SendDataRequestSchema(BaseModel):
    task_id: str
    task_name: Optional[str] = Field(title="任务名称")
    username: Optional[str] = Field(title="用户名")
    mac_address: str = Field(title="Mac地址")
    md5: str = Field(title="文件md5值")
    icem_hardware_level: Literal['low', 'medium', 'high'] = Field(title="icem硬件配置等级: low、medium、high")
    icem_params: Optional[dict[str, str]] = Field(title="icem参数")
    fluent_hardware_level: Literal['low', 'medium', 'high'] = Field(title="fluent硬件配置等级: low、medium、high")
    fluent_params: dict[str, str] = Field(title="fluent参数")


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
        query_data = {"task_id_list": task_id_list}
        return query_data

    async def get(self, task_id_list: List[str]):
        response = copy(self.response)
        pqc = pydantic_queryset_creator(Uknow)
        if isinstance(task_id_list, list) and len(task_id_list) == 0:
            query_set = Uknow.filter()
        else:
            query_set = Uknow.filter(task_id__in=task_id_list)
        query_data = await pqc.from_queryset(query_set)
        response["data"] = query_data.dict()['__root__']
        response['message'] = '查询成功'
        return response
