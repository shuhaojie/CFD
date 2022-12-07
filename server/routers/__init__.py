from fastapi import APIRouter

from apps.task.views import router as task_router
from config import configs
from .ping_views import router as ping_router


def router_init(app):
    apps_router = APIRouter()
    apps_router.include_router(task_router)

    app.include_router(apps_router,
                       prefix=configs.API_V1_STR)
    app.include_router(ping_router)
