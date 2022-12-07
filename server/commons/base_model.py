#!/usr/bin/python
import uuid

from tortoise import fields
from tortoise.models import Model

from utils.constant import MyConstant


class MyAbstractBaseModel(Model):
    uuid = fields.CharField(max_length=MyConstant.MAX_LENGTH, pk=True, default=uuid.uuid1)
    timestamp = fields.DatetimeField(description='创建时间', auto_now_add=True, null=True)

    class Meta:
        abstract = True
