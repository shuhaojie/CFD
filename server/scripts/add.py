import os
import sys
import uuid
import hashlib
from tortoise import Tortoise, run_async
from passlib.context import CryptContext

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from apps.models import Uknow  # noqa
from dbs.database import TORTOISE_ORM
from config import Settings  # noqa


def get_password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def get_md5():
    with open(r"C:\workspaces\data\monitor\a8d06526-75f9-11ed-bac6-e0d045dbb4d7.zip", "rb") as f:
        current_bytes = f.read()
        current_hash = hashlib.md5(current_bytes).hexdigest()
    return current_hash


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    # https://tortoise-orm.readthedocs.io/en/latest/examples/basic.html#router

    await Uknow.create(
        task_id=str(uuid.uuid1()),
        md5=get_md5(),
        hardware='low',
    )

if __name__ == "__main__":
    run_async(run())
