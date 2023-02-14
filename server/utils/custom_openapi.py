from fastapi.openapi.utils import get_openapi
from config import configs


def init_openapi(app):
    """初始化openapi"""

    def custom_openapi():
        """去除422响应"""
        if app.openapi_schema:
            return app.openapi_schema
        if configs.ENVIRONMENT == 'development':
            title = "CFD自动化平台api-研发环境"
        elif configs.ENVIRONMENT == 'production':
            title = "CFD自动化平台api-正式环境"
        else:
            title = "CFD自动化平台api-测试环境"
        openapi_schema = get_openapi(
            title=title,
            description="模块接口文档",
            version="1.0.0",
            routes=app.routes,
        )
        # look for the error 422 and removes it
        for path in openapi_schema["paths"]:
            for method in openapi_schema["paths"][path]:
                try:
                    del openapi_schema["paths"][path][method]["responses"]["422"]
                except KeyError:
                    pass
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
