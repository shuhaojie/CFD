import os
import uvicorn
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi_admin.app import app as admin_app
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from dbs.database import db_init
from scripts.add import db_table_init, run
from logs import log_init, api_log
from middleware import middleware_init
from utils.common_util import write_log
from routers import router_init
from utils.custom_openapi import init_openapi
from config import configs
from apps.admin.providers import LoginProvider
from apps.models import Admin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def conf_init(app):
    api_log.info(msg=f'Start app with {configs.ENVIRONMENT} environment')
    if configs.ENVIRONMENT == 'production':
        app.docs_url = None
        app.redoc_url = None
        app.debug = False


async def start_event():
    await write_log(msg='系统启动')


def create_app():
    app = FastAPI(title="CFD项目api接口",
                  description="模块接口文档",
                  version="1.0.0",
                  # on_startup=[start_event],
                  )

    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(BASE_DIR, "apps", "admin", "static")),
        name="static",
    )

    # 初始化日志
    log_init()

    # 加载配置
    conf_init(app)

    # 初始化路由配置
    router_init(app)

    # 初始化中间件
    middleware_init(app)

    # 数据库连接
    db_init(app)

    # 自定义openapi
    init_openapi(app)

    # 数据入库
    # db_table_init()

    @app.on_event("startup")
    async def startup():
        if configs.ENVIRONMENT == 'local':
            r = redis.from_url(
                f"redis://:{configs.REDIS_PASSWD}@{configs.REDIS_HOST}/0",
                decode_responses=True,
                encoding="utf8",
            )
        else:
            r = redis.from_url(
                f"redis://{configs.REDIS_HOST}/0",
                decode_responses=True,
                encoding="utf8",
            )

        await admin_app.configure(
            default_locale='zh_CN',
            logo_url="http://www.unionstrongtech.com.cn/header/logo.png",
            template_folders=[os.path.join(BASE_DIR, "apps", "admin", "templates")],
            favicon_url="http://www.unionstrongtech.com.cn/header/logo.png",
            providers=[
                LoginProvider(
                    login_logo_url="http://www.unionstrongtech.com.cn/header/logo.png",
                    admin_model=Admin,
                )
            ],
            redis=r,
        )

    app.mount("/admin", admin_app)

    @app.get("/")
    async def index():
        return RedirectResponse(url="/admin")

    return app


app = create_app()


# 自定义异常
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(exc: RequestValidationError):
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=jsonable_encoder({"status": False,
                                                  "code": 412,
                                                  "message": "提交数据异常",
                                                  "data": exc.errors()}),
                        )


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0', port=8000, debug=True, reload=True)

    errors = [{'loc': ('body', 'name'), 'msg': 'field required', 'type': 'value_error.missing'},
              {'loc': ('body', 'picture'), 'msg': 'field required', 'type': 'value_error.missing'}]
