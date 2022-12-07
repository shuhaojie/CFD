import os
import sys
from tortoise import Tortoise, run_async
from passlib.context import CryptContext

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from apps.models import Task  # noqa
from dbs.database import TORTOISE_ORM
from config import Settings  # noqa


def get_password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    # https://tortoise-orm.readthedocs.io/en/latest/examples/basic.html#router

    # 1.新增分类
    # await Category.create(name="Test")
    # 2.新增标签
    # await Tag.create(name="Test")
    # 3.新增用户
    # hash_password = get_password_hash("haojie")
    # await User.create(username="haojie",
    #                   password=hash_password,
    #                   )
    # 4.新增文章
    # category = await Category.filter(name="Test").first()
    # user = await User.filter(username="haojie").first()
    # await Article.create(
    #     title="second article",
    #     body="This is the second article",
    #     category_id=category.uuid,
    #     author_id=user.uuid,
    # )

    # 5. article和tag的ManyToMany入库
    # article = await Article.filter(title="Test").first()
    # tag = await Tag.filter(name="Test").first()
    # await article.tag.add(tag)

    a = await Task.filter(task_id="0")
    print(len(a))

if __name__ == "__main__":
    run_async(run())
