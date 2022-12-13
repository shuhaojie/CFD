#!/usr/bin/python
import uuid
from tortoise import fields
from tortoise.models import Model

from utils.constant import MyConstant


class AbstractBaseModel(Model):
    uuid = fields.CharField(max_length=MyConstant.MAX_LENGTH, pk=True, default=uuid.uuid1())

    class Meta:
        abstract = True
