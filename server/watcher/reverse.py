"""
轮询状态的核心代码
"""
import os
import json
import sys
import requests
from tortoise import Tortoise, run_async

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config import configs  # noqa
from apps.models import Task, Uknow, Queue  # noqa
from dbs.database import TORTOISE_ORM  # noqa


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    # 1. 先拿到token

    base_url = 'http://127.0.0.1:8000/reverse_status'
    headers = ""
    # https://stackoverflow.com/a/35851514/10844937
    params = {'id_list': json.dumps(["a5b54697-7601-11ed-9d03-e0d045dbb4d7"])}
    r = requests.get(
        url=base_url,
        headers=headers,
        params=params
    )
    print(r.status_code)
    print(r.text)


if __name__ == "__main__":
    run_async(run())
