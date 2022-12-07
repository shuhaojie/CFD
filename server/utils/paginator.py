import datetime
from math import ceil
from typing import Type, Union

from tortoise.models import Model
from tortoise.queryset import QuerySet


async def tortoise_paginate(query: Union[QuerySet, Type[Model]], page_index: int = 1, page_per_count: int = 10,
                            model=None, customer_model=None) -> dict:
    """
     :param query: tortoise的query查询
    :param page_index: 当前页
    :param page_per_count: 每页显示条数,默认20
    """
    if not isinstance(query, QuerySet):
        query = query.all()

    offset = (page_index - 1) * page_per_count
    limit = page_per_count
    total = await query.count()
    items = await query.offset(offset).limit(limit).all()
    if model:

        for i in items:
            if hasattr(i, "operation_user") and i.operation_user:
                i.operation_user = await model.filter(uuid=i.operation_user).first()
            if hasattr(i, "customer") and i.order_time and isinstance(i.order_time, datetime.datetime):
                i.order_time = datetime.datetime.strftime(i.order_time, "%Y-%m-%d %H:%M:%S")
            if hasattr(i, "customer") and i.customer:
                i.customer = await customer_model.filter(uuid=i.customer).first()
            if hasattr(i, "password") and i.password:
                i.password = "******"
            # if i.operation_user:
            #     print(">>>>", await model.filter(uuid=i.operation_user).first())
            #     i.operation_user =await model.filter(uuid=i.operation_user).first()
    data = {
        "data": items,
        "total": total,
        "page_index": page_index,
        "page_count": int(ceil(total / int(page_per_count))),
        "has_previous": page_index > 1,
        "has_next": page_index < int(ceil(total / int(page_per_count))),
    }
    return data
