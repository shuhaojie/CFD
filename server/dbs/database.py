from tortoise.contrib.fastapi import register_tortoise
from config import configs
from tortoise import Tortoise

TORTOISE_ORM = {
    "connections": {
        "default": f"mysql://{configs.MYSQL_USER}:{configs.MYSQL_PASSWORD}@{configs.MYSQL_SERVER}:{configs.MYSQL_PORT}/{configs.MYSQL_DB}"},
    "apps": {
        "models": {
            "models": ["apps.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "timezone": "Asia/shanghai"

}


def db_init(app):
    """orm数据库注册"""
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    )


async def database_init():
    await Tortoise.init(
        # 指定mysql信息
        db_url=f"mysql://{configs.MYSQL_USER}:{configs.MYSQL_PASSWORD}@{configs.MYSQL_SERVER}:{configs.MYSQL_PORT}/{configs.MYSQL_DB}",
        # 指定models
        modules={'models': ['apps.models']}
    )


if __name__ == "__main__":
    token = {
        "expiredTime": "1506433269",
        "expiration": "2017-09-26T13:41:09Z",
        "credentials": {
            "sessionToken": "sdadffwe2323er4323423",
            "tmpSecretId": "VpxrX0IMC pHXWL0Wr3KQNCqJix1uhMqD",
            "tmpSecretKey": "VpxrX0IMC pHXWL0Wr3KQNCqJix1uhMqD"
        }
    }
