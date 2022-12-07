#!/usr/bin/python
from functools import lru_cache
from typing import List, Optional, Tuple, Type
from pydantic import BaseModel, Field, create_model
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from tortoise.models import Model
from tortoise import Tortoise


class RequestValidationErrorSchema(BaseModel):
    loc: Tuple[str, ...] = Field(..., title="异常参数位置与名称", description="首位表示参数来源[query,path,body...],末尾表示参数名称")
    msg: str = Field(..., title="异常信息")
    type: str = Field(..., title="异常类型")


class BaseResponse(BaseModel):
    """通用响应"""
    status: Optional[bool] = Field(True, title="响应状态")
    code: Optional[int] = Field(200, title="响应状态码")
    message: Optional[str] = Field('', title="提示信息")


class RequestValidationErrorResponse(BaseResponse):
    status: Optional[bool] = Field(False, title="响应状态")
    code: Optional[int] = Field(412, title="响应状态码")
    data: List[RequestValidationErrorSchema] = Field(..., title="异常详情列表")


@lru_cache
def get_response_pydantic(models_obj: Type[Model], exclude: Tuple[str, ...] = None) -> Type[BaseModel]:
    """
    根据model生成响应pydantic
    """
    if exclude:
        my_model_pydantic = pydantic_model_creator(models_obj, exclude=exclude,
                                                   name=f".{models_obj.__name__}_pydantic")
    else:
        my_model_pydantic = pydantic_model_creator(models_obj,
                                                   name=f".{models_obj.__name__}_pydantic")
    response_pydantic = create_model(
        __model_name=f"{models_obj.__name__}_response_pydantic",
        data=(Optional[my_model_pydantic], Field(None, title="数据")),
        __base__=BaseResponse)
    return response_pydantic


@lru_cache
def get_serialize_pydantic(models_obj: Type[Model], exclude: Tuple[str, ...] = None):
    Tortoise.init_models(["apps.models"], "models")  # 防止外键被忽略
    if exclude:
        my_model_pydantic = pydantic_model_creator(models_obj, exclude=exclude,
                                                   name=f".{models_obj.__name__}_pydantic")
    else:
        my_model_pydantic = pydantic_model_creator(models_obj,
                                                   name=f".{models_obj.__name__}_pydantic")
    response_pydantic = create_model(
        __model_name=f"{models_obj.__name__}_response_pydantic",
        data=(Optional[List[my_model_pydantic]], Field(None, title="数据")),
        __base__=BaseResponse)
    return response_pydantic
