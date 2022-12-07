import os
import sys
from tortoise import Tortoise, run_async

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from apps.models import Category, Article  # noqa
from dbs.database import TORTOISE_ORM  # noqa
from tortoise.contrib.pydantic import pydantic_queryset_creator, pydantic_model_creator  # noqa


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    pqc = pydantic_model_creator(Article)
    query_set = Article.filter()
    tourpy = await pqc.from_queryset(query_set)


if __name__ == "__main__":
    run_async(run())
