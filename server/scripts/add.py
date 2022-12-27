import os
import sys
from tortoise import Tortoise, run_async
from passlib.context import CryptContext

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from apps.models import FluentProf, Admin, FluentHardware, IcemHardware
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
    if len(query) == 1:
        pass
    else:
        username = configs.ADMIN_USERNAME
        passwd = configs.ADMIN_PASSWD
        hash_password = get_password_hash(passwd)
        await Admin.create(
            username=username,
            password=hash_password,
        )

    # 3. 入库FluentHardware
    query = await FluentHardware.all()
    if len(query) == 3:
        pass
    else:
        hardware_list = [
            {
                'id': 1,
                'level': 'low',
                'fs_instance_type': 'b1.c1.24',
                'cpu_frequency': 2.6,
                'cpu_model': 'Intel Xeon Icelake 8350C 32C',
                'v_cpu': 24,
                'memory': 48,
                'price': 4.8048,
                'system_platform': 'CentOS',
            },
            {
                'id': 2,
                'level': 'medium',
                'fs_instance_type': 'b1.c1.32',
                'cpu_frequency': 2.6,
                'cpu_model': 'Intel Xeon Icelake 8350C 32C',
                'v_cpu': 32,
                'memory': 64,
                'price': 6.4064,
                'system_platform': 'CentOS',
            },
            {
                'id': 3,
                'level': 'high',
                'fs_instance_type': 'b1.c1.48',
                'cpu_frequency': 2.6,
                'cpu_model': 'Intel Xeon Icelake 8350C 32C',
                'v_cpu': 48,
                'memory': 96,
                'price': 9.6096,
                'system_platform': 'CentOS',
            },
        ]
        for hardware in hardware_list:
            await FluentHardware.create(
                **hardware
            )
            await IcemHardware.create(
                **hardware
            )


if __name__ == "__main__":
    run_async(run())
