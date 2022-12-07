#!/usr/bin/python
import uuid

from tortoise import fields
from tortoise.models import Model

from utils.constant import MyConstant

from tortoise import fields
from tortoise.models import Model

from utils.constant import MyConstant


class AbstractBaseModel(Model):
    task_id = fields.CharField(max_length=MyConstant.MAX_LENGTH, pk=True)
    create_time = fields.DatetimeField(description='创建时间', auto_now_add=True)
    update_time = fields.DatetimeField(description='更新时间', auto_now=True)
    is_delete = fields.BooleanField(description='是否删除', null=True, default=False)
    comment = fields.TextField(description='备注', null=True)

    class Meta:
        abstract = True
