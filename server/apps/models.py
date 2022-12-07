import uuid
from tortoise import fields
from tortoise.models import Model

from utils.constant import MyConstant, TaskStatus
from commons.base_model import AbstractBaseModel


class Task(AbstractBaseModel):
    status = fields.CharField(max_length=MyConstant.MAX_LENGTH, description="脚本执行状态", default=TaskStatus.PENDING)

    class Meta:
        table = "task"
        table_description = "脚本执行任务"


class Uknow(AbstractBaseModel):
    status = fields.CharField(description="UKnow数据上传状态",
                              max_length=MyConstant.MAX_LENGTH,
                              default='pending')
    hardware = fields.CharField(description="硬件配置", max_length=MyConstant.MAX_LENGTH)
    md5 = fields.CharField(description="md5值", max_length=MyConstant.MAX_LENGTH)

    class Meta:
        table = "uknow"
        table_description = "Uknow数据上传"


class Queue(AbstractBaseModel):
    class Meta:
        table = "queue"
        table_description = "排队队列"
