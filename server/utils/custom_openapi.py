from fastapi.openapi.utils import get_openapi


def init_openapi(app):
    """初始化openapi"""

    def custom_openapi():
        """去除422响应"""
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="CFD自动化平台api",
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
