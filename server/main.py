import uvicorn
from fastapi import FastAPI
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dbs.database import db_init
from logs import log_init, api_log
from middleware import middleware_init
from utils.common_util import write_log
from routers import router_init
from utils.custom_openapi import init_openapi
from fastapi_utils.tasks import repeat_every


def conf_init(app):
    from config import configs
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
                  on_startup=[start_event],
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
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, debug=True, reload=True)

    errors = [{'loc': ('body', 'name'), 'msg': 'field required', 'type': 'value_error.missing'},
              {'loc': ('body', 'picture'), 'msg': 'field required', 'type': 'value_error.missing'}]
