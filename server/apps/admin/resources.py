import datetime
import os
import pytz
from typing import List
from starlette.requests import Request
from apps.models import Uknow, FluentHardware, IcemHardware
from config import configs
from utils.constant import Status
from fastapi_admin.app import app
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.resources import Action, Field, Dropdown, Model, ToolbarAction, ComputeField
from fastapi_admin.widgets import filters, inputs
from tortoise import Tortoise
from dbs.database import TORTOISE_ORM, database_init

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload = FileUpload(uploads_dir=os.path.join(BASE_DIR, "static", "uploads"))


class SystemComputeFields(ComputeField):
    """
    系统字段展示
    """

    async def get_value(self, request: Request, obj: dict):
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await database_init()
        system_query = await Uknow.filter(id=obj.get("id", None)).first()
        await Tortoise.close_connections()
        if system_query:
            return system_query.task_id
        else:
            return


class DateTimeComputeFields(ComputeField):
    """
    Radio类型返回字段展示
    """

    async def get_value(self, request: Request, obj: dict):
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await database_init()
        system_query = await Uknow.filter(id=obj.get("id", None)).first()
        await Tortoise.close_connections()
        if system_query.create_time:
            return system_query.create_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return '-'


class IcemLevelComputeFields(ComputeField):
    """
    Radio类型返回字段展示
    """

    async def get_value(self, request: Request, obj: dict):
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await database_init()
        query = await Uknow.filter(id=obj.get("id", None)).first()
        await Tortoise.close_connections()
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
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await database_init()
        query = await Uknow.filter(id=obj.get("id", None)).first()
        await Tortoise.close_connections()
        if query.fluent_hardware_level == 'low':
            fluent = '低'
        elif query.fluent_hardware_level == 'medium':
            fluent = '中'
        else:
            fluent = '高'
        if query.icem_hardware_level == 'low':
            icem = '低'
        elif query.icem_hardware_level == 'medium':
            icem = '中'
        else:
            icem = '高'
        return f'{fluent}/{icem}'


class StatusComputeFields(ComputeField):
    async def get_value(self, request: Request, obj: dict):
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await database_init()
        query = await Uknow.filter(id=obj.get("id", None)).first()
        await Tortoise.close_connections()
        if not query.create_time and query.icem_status == Status.QUEUE:
            return '任务排队中'
        if not query.create_time:
            return '任务失败'
        total_seconds = (
                datetime.datetime.now().replace(tzinfo=pytz.timezone('UTC')) - query.create_time).total_seconds()
        if query.data_status == 'success':
            if not query.icem_status:
                return '数据上传成功'
            else:
                if query.icem_status == Status.PENDING:
                    if total_seconds > 3600:
                        return 'Icem处理失败'
                    else:
                        return 'Icem处理中'
                elif query.icem_status == Status.FAIL:
                    return 'Icem处理失败'
                elif query.icem_status == Status.QUEUE:
                    return f'任务排队中'
                else:
                    if not query.fluent_status:
                        return 'Icem处理成功'
                    else:
                        if query.fluent_status == Status.PENDING:
                            if total_seconds > 3600:
                                return 'Fluent处理失败'
                            else:
                                return 'Fluent处理中'
                        elif query.fluent_status == Status.FAIL:
                            return 'Fluent处理失败'
                        else:
                            return '任务成功'
        elif query.data_status == Status.PENDING:
            return '数据上传中'
        else:
            return query.data_code


class TotalTimeComputeFields(ComputeField):
    async def get_value(self, request: Request, obj: dict):
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await database_init()
        query = await Uknow.filter(id=obj.get("id", None)).first()
        await Tortoise.close_connections()
        if not query.create_time:
            total_seconds = 0
        else:
            total_seconds = ((datetime.datetime.now()).replace(
                tzinfo=pytz.timezone('UTC')) - query.create_time).total_seconds()
        # 如果有fluent_end, 优先用这个值
        if query.fluent_end:
            total_seconds = (query.fluent_end - query.create_time).total_seconds()
        # 如果fluent任务是pending, 并且时间大于3600, 此时时间应该为3600
        elif query.fluent_status == Status.PENDING and total_seconds > 3600:
            total_seconds = 3600
        else:
            # 如果Icem任务失败, 需要用Icem的时间
            if query.icem_status == Status.FAIL:
                if query.create_time:
                    total_seconds = (query.icem_end - query.create_time).total_seconds()
                else:
                    total_seconds = 0
            elif query.icem_status == Status.PENDING and total_seconds > 3600:
                total_seconds = 3600
            else:
                if query.create_time:
                    total_seconds = ((datetime.datetime.now()).replace(
                        tzinfo=pytz.timezone('UTC')) - query.create_time).total_seconds()
                else:
                    total_seconds = 0
        m, s = divmod(total_seconds, 60)
        return f'{int(m)}分{int(s)}秒'


class LogFileComputeFields(ComputeField):
    async def get_value(self, request: Request, obj: dict):
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await database_init()
        query = await Uknow.filter(id=obj.get("id", None)).first()
        await Tortoise.close_connections()
        if query.fluent_result_file_path:
            return query.fluent_result_file_path
        if query.icem_log_file_path:
            return '-'
        if query.fluent_log_file_path:
            return '-'


class WidgetComputeFields(ComputeField):
    async def get_value(self, request: Request, obj: dict):
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await database_init()
        query = await Uknow.filter(id=obj.get("id", None)).first()
        await Tortoise.close_connections()
        if query.widgets:
            return f'{query.widgets}元'
        else:
            return '-'


@app.register
class UknowResource(Model):
    label = "任务状态"
    model = Uknow
    icon = "fas fa-home"
    url = "/admin"
    page_pre_title = f"uknow数据列表-{configs.ENVIRONMENT}"
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
        SystemComputeFields(name="id", label="id", input_=inputs.DisplayOnly()),
        Field(name="order_id", label="订单id", input_=inputs.DisplayOnly()),
        Field(name="username", label="操作人员", input_=inputs.DisplayOnly()),
        DateTimeComputeFields(name="create_time", label="创建时间", input_=inputs.DisplayOnly()),
        StatusComputeFields(name="data_status", label="任务状态", input_=inputs.DisplayOnly()),
        TotalTimeComputeFields(name="fluent_duration", label="任务耗时", input_=inputs.DisplayOnly()),
        WidgetComputeFields(name="widgets", label="任务花费", input_=inputs.DisplayOnly()),
        Field(name="fluent_prof", label="prof文件", input_=inputs.DisplayOnly()),
        FluentLevelComputeFields(name="fluent_hardware_level", label="硬件配置", input_=inputs.DisplayOnly()),
        LogFileComputeFields(name="fluent_result_file_path", label="结果文件", input_=inputs.DisplayOnly()),
    ]

    async def get_toolbar_actions(self, request: Request) -> List[ToolbarAction]:
        return []

    async def cell_attributes(self, request: Request, obj: dict, field: Field) -> dict:
        if field.name == 'data_status' and obj.get("fluent_status") == Status.SUCCESS:
            return {"class": "text-green"}
        return await super().cell_attributes(request, obj, field)

    async def get_actions(self, request: Request) -> List[Action]:
        return []

    async def get_bulk_actions(self, request: Request) -> List[Action]:
        return []


class FrequencyComputeFields(ComputeField):
    async def get_value(self, request: Request, obj: dict):
        await database_init()
        query = await FluentHardware.filter(id=obj.get("id", None)).first()
        await Tortoise.close_connections()
        return f'{query.cpu_frequency}GHz'


@app.register
class Content(Dropdown):
    class Fluent(Model):
        label = "Fluent"
        model = FluentHardware
        icon = "fas fa-home"
        page_pre_title = "Fluent硬件配置表"
        fields = [
            Field(name="level", label="硬件级别", input_=inputs.DisplayOnly()),
            Field(name="process_num", label="并发数", input_=inputs.DisplayOnly()),
            Field(name="enum", label="求解器", input_=inputs.DisplayOnly()),
            FrequencyComputeFields(name="cpu_frequency", label="CPU核心频率", input_=inputs.DisplayOnly()),
            Field(name="cpu_model", label="CPU型号", input_=inputs.DisplayOnly()),
            Field(name="v_cpu", label="虚拟CPU数", input_=inputs.DisplayOnly()),
            Field(name="memory", label="显存数", input_=inputs.DisplayOnly()),
            Field(name="price", label="价格(元/小时)", input_=inputs.DisplayOnly()),
            Field(name="system_platform", label="操作系统", input_=inputs.DisplayOnly()),
        ]

        async def get_toolbar_actions(self, request: Request) -> List[ToolbarAction]:
            return []

        async def get_actions(self, request: Request) -> List[Action]:
            return []

        async def get_bulk_actions(self, request: Request) -> List[Action]:
            return []

    class Icem(Model):
        label = "Icem"
        model = IcemHardware
        page_pre_title = "uknow数据列表"
        fields = [
            Field(name="level", label="硬件级别", input_=inputs.DisplayOnly()),
            FrequencyComputeFields(name="cpu_frequency", label="CPU核心频率", input_=inputs.DisplayOnly()),
            Field(name="cpu_model", label="CPU型号", input_=inputs.DisplayOnly()),
            Field(name="v_cpu", label="虚拟CPU数", input_=inputs.DisplayOnly()),
            Field(name="memory", label="显存数", input_=inputs.DisplayOnly()),
            Field(name="price", label="价格(元/小时)", input_=inputs.DisplayOnly()),
            Field(name="system_platform", label="操作系统", input_=inputs.DisplayOnly()),
        ]

        async def get_toolbar_actions(self, request: Request) -> List[ToolbarAction]:
            return []

        async def get_actions(self, request: Request) -> List[Action]:
            return []

        async def get_bulk_actions(self, request: Request) -> List[Action]:
            return []

    label = "硬件配置"
    icon = "fas fa-bars"
    resources = [Fluent, Icem]
