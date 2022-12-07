import os
import sys
from functools import lru_cache
from tortoise.contrib.pydantic import pydantic_queryset_creator
from typing import Tuple, Type, Optional
from tortoise.models import Model
from pydantic import Field, create_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from apps.models import Category, User, Article, Tag  # noqa
from commons.schemas import BaseResponse  # noqa


@lru_cache
def get_serialize_pydantic(models_obj: Type[Model], exclude: Tuple[str, ...] = None):
    if exclude:
        my_model_pydantic = pydantic_queryset_creator(models_obj, exclude=exclude,
                                                      name=f".{models_obj.__name__}_pydantic")
    else:
        my_model_pydantic = pydantic_queryset_creator(models_obj,
                                                      name=f".{models_obj.__name__}_pydantic")
    # my_model_pydantic.dict()
    # response_pydantic = create_model(
    #     __model_name=f"{models_obj.__name__}_response_pydantic",
    #     data=(Optional[my_model_pydantic], Field(None, title="数据")),
    #     __base__=BaseResponse)


if __name__ == "__main__":
    get_serialize_pydantic(Article)
