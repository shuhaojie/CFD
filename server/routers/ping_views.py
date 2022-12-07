#!/usr/bin/python
# -*- coding: utf-8 -*-

import pickle

from fastapi import APIRouter

from commons.schemas import BaseResponse
from config import configs

from utils.constant import HTTP

router = APIRouter()


@router.get("/ping", response_model=BaseResponse)
async def ping():
    """
    测试模块连通性
    """

    return {'status_code': HTTP.HTTP_200_OK, "msg": "系统配置信息如下", 'data': configs.dict()}
