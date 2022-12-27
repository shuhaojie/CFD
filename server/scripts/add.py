import os
import sys
from tortoise import Tortoise, run_async
from passlib.context import CryptContext

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from apps.models import FluentProf, Admin
from dbs.database import TORTOISE_ORM
from config import configs


def get_password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    # 1. 入库FluentProf
    query = await FluentProf.all()
    if len(query) == 5:
        pass
    else:
        prof_list = [{'ACA': 'ACA_from_ICA_fourier_mass.prof'},
                     {'BA': 'BA_from_ICA_fourier_mass.prof'},
                     {'ICA': 'ICA_from_ICA_fourier_mass.prof'},
                     {'MCA': 'MCA_from_ICA_fourier_mass.prof'},
                     {'VA': 'VA_from_ICA_fourier_mass.prof'}]
        for prof in prof_list:
            prof_name = list(prof.keys())[0]
            prof_path = list(prof.values())[0]
            await FluentProf.create(
                prof_name=prof_name,
                prof_path=prof_path,
            )

    # 2. 入库admin页面
    query = await Admin.all()
    if len(query) == 2:
        pass
    else:
        username = configs.ADMIN_USERNAME
        passwd = configs.ADMIN_PASSWD
        hash_password = get_password_hash(passwd)
        await Admin.create(
            username=username,
            password=hash_password,
        )


if __name__ == "__main__":
    run_async(run())
