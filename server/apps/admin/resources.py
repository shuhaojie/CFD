import os
from typing import List

from starlette.requests import Request

from apps.models import Admin, Uknow
from fastapi_admin.app import app
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.resources import Action, Field, Link, Model, ToolbarAction, ComputeField
from fastapi_admin.widgets import displays, filters, inputs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload = FileUpload(uploads_dir=os.path.join(BASE_DIR, "static", "uploads"))


@app.register
class Dashboard(Link):
    label = "Dashboard"
    icon = "fas fa-home"
    url = "/admin"


class SystemComputeFields(ComputeField):
    """
    系统字段展示
    """

    async def get_value(self, request: Request, obj: dict):
        system_query = await Uknow.filter(uuid=obj.get("uuid", None)).first()
        if system_query:
            return system_query.task_id
        else:
            return


class DateTimeComputeFields(ComputeField):
    """
    Radio类型返回字段展示
    """

    async def get_value(self, request: Request, obj: dict):
        system_query = await Uknow.filter(uuid=obj.get("uuid", None)).first()
        if system_query:
            return system_query.create_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return


class IcemLevelComputeFields(ComputeField):
    """
    Radio类型返回字段展示
    """

    async def get_value(self, request: Request, obj: dict):
        query = await Uknow.filter(uuid=obj.get("uuid", None)).first()
        if query.icem_hardware_level == 'low':
            return '低'
        elif query.icem_hardware_level == 'medium':
            return '中'
        else:
            return '高'


class FluentLevelComputeFields(ComputeField):
    """
    Radio类型返回字段展示
    """

    async def get_value(self, request: Request, obj: dict):
        query = await Uknow.filter(uuid=obj.get("uuid", None)).first()
        if query.fluent_hardware_level == 'low':
            return '低'
        elif query.fluent_hardware_level == 'medium':
            return '中'
        else:
            return '高'


class StatusComputeFields(ComputeField):
    async def get_value(self, request: Request, obj: dict):
        query = await Uknow.filter(uuid=obj.get("uuid", None)).first()
        if query.data_status == 'success':
            if not query.icem_status:
                return '数据上传成功'
            else:
                if query.icem_status == 'pending':
                    return 'Icem处理中'
        elif query.data_status == 'pending':
            return '数据上传中'
        else:
            return query.data_code


@app.register
class UknowResource(Model):
    label = "Uknow"
    model = Uknow
    icon = "fas fa-bars"
    page_pre_title = "uknow数据列表"
    filters = [
        filters.Search(
            name="username",
            label="username",
            search_mode="contains",
            placeholder="请输入用户名......",
        ),
        filters.Date(name="create_time", label="date"),
    ]
    fields = [
        SystemComputeFields(name="uuid", label="id", input_=inputs.DisplayOnly()),
        Field(name="task_id", label="任务id", input_=inputs.DisplayOnly()),
        Field(name="task_name", label="任务名称", input_=inputs.DisplayOnly()),
        Field(name="username", label="用户名", input_=inputs.DisplayOnly()),
        DateTimeComputeFields(name="create_time", label="创建时间", input_=inputs.DisplayOnly()),
        StatusComputeFields(name="data_status", label="任务状态", input_=inputs.DisplayOnly()),
        # IcemLevelComputeFields(name="icem_hardware_level", label="Icem硬件等級", input_=inputs.DisplayOnly()),
        # FluentLevelComputeFields(name="fluent_hardware_level", label="Fluent硬件等級", input_=inputs.DisplayOnly()),
        Field(name="fluent_result_file_path", label="结果文件", input_=inputs.DisplayOnly()),
        Field(name="fluent_log_file_path", label="日志文件", input_=inputs.DisplayOnly()),
    ]

    async def get_toolbar_actions(self, request: Request) -> List[ToolbarAction]:
        return []

    async def cell_attributes(self, request: Request, obj: dict, field: Field) -> dict:
        return await super().cell_attributes(request, obj, field)

    async def get_actions(self, request: Request) -> List[Action]:
        return []

    async def get_bulk_actions(self, request: Request) -> List[Action]:
        return []


@app.register
class GithubLink(Link):
    label = "GitHub"
    url = "http://172.16.1.232:8443/shuhaojie/CFD"
    icon = "fab fa-github"
    target = "_blank"


class ComputeField(Field):
    async def get_value(self, request: Request, obj: dict):
        return obj.get(self.name)
