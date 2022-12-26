import datetime
import os
import pytz
from typing import List
from starlette.requests import Request
from apps.models import Uknow, FluentHardware, IcemHardware
from utils.constant import Status
from fastapi_admin.app import app
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.resources import Action, Field, Dropdown, Model, ToolbarAction, ComputeField
from fastapi_admin.widgets import filters, inputs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload = FileUpload(uploads_dir=os.path.join(BASE_DIR, "static", "uploads"))


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
        if system_query.create_time:
            return system_query.create_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return '-'


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
                elif query.icem_status == 'fail':
                    return 'Icem处理失败'
                elif query.icem_status == 'pending':
                    queur_number = query.task_queue
                    return f'任务排队中, 排队号{queur_number}'
                else:
                    if not query.fluent_status:
                        return 'Icem处理成功'
                    else:
                        if query.fluent_status == 'pending':
                            return 'Fluent处理中'
                        elif query.fluent_status == 'fail':
                            return 'Fluent处理失败'
                        else:
                            return '任务成功'
        elif query.data_status == 'pending':
            return '数据上传中'
        else:
            return query.data_code


class TotalTimeComputeFields(ComputeField):
    async def get_value(self, request: Request, obj: dict):
        query = await Uknow.filter(uuid=obj.get("uuid", None)).first()
        if query.fluent_end:
            total_seconds = (query.fluent_end - query.create_time).total_seconds()
        else:
            if query.create_time:
                total_seconds = ((datetime.datetime.now() + datetime.timedelta(hours=-8)).replace(
                    tzinfo=pytz.timezone('UTC')) - query.create_time).total_seconds()
            else:
                total_seconds = 0
        m, s = divmod(total_seconds, 60)
        return f'{int(m)}分{int(s)}秒'


@app.register
class UknowResource(Model):
    label = "任务状态"
    model = Uknow
    icon = "fas fa-home"
    url = "/admin"
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
        TotalTimeComputeFields(name="fluent_duration", label="任务耗时", input_=inputs.DisplayOnly()),
        Field(name="fluent_result_file_path", label="结果文件", input_=inputs.DisplayOnly()),
        Field(name="fluent_log_file_path", label="日志文件", input_=inputs.DisplayOnly()),
    ]

    async def get_toolbar_actions(self, request: Request) -> List[ToolbarAction]:
        return []

    async def cell_attributes(self, request: Request, obj: dict, field: Field) -> dict:
        if field.name == 'data_status' and obj.get("fluent_status") == Status.SUCCESS:
            return {"class": "text-green"}
        if field.name == 'data_status' and (
                obj.get("fluent_status") == Status.FAIL or obj.get("icem_status") == Status.FAIL):
            return {"class": "text-red"}
        return await super().cell_attributes(request, obj, field)

    async def get_actions(self, request: Request) -> List[Action]:
        return []

    async def get_bulk_actions(self, request: Request) -> List[Action]:
        return []


@app.register
class Content(Dropdown):
    class Fluent(Model):
        label = "Fluent"
        model = FluentHardware

    class Icem(Model):
        label = "Icem"
        model = IcemHardware

    label = "硬件配置"
    icon = "fas fa-bars"
    resources = [Fluent, Icem]
