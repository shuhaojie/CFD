import uuid
from fastapi import Depends, Form
from typing import Type
from aioredis import Redis
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_401_UNAUTHORIZED
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin import constants
from fastapi_admin.depends import get_current_admin, get_redis, get_resources
from fastapi_admin.i18n import _
from fastapi_admin.models import AbstractAdmin
from fastapi_admin.template import templates
from fastapi_admin.utils import check_password


class LoginProvider(UsernamePasswordProvider):

    async def password(
            self,
            request: Request,
            old_password: str = Form(...),
            new_password: str = Form(...),
            re_new_password: str = Form(...),
            admin: AbstractAdmin = Depends(get_current_admin),
            resources=Depends(get_resources),
    ):
        return await self.logout(request)

    async def login(self, request: Request, redis: Redis = Depends(get_redis)):
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        remember_me = form.get("remember_me")
        admin = await self.admin_model.get_or_none(username=username)
        if not admin or not check_password(password, admin.password):
            return templates.TemplateResponse(
                self.template,
                status_code=HTTP_401_UNAUTHORIZED,
                context={"request": request, "error": _("login_failed")},
            )
        response = RedirectResponse(url=request.app.admin_path, status_code=HTTP_303_SEE_OTHER)
        if remember_me == "on":
            expire = 3600 * 24 * 30
            response.set_cookie("remember_me", "on")
        else:
            expire = 3600
            response.delete_cookie("remember_me")
        token = uuid.uuid4().hex
        response.set_cookie(
            self.access_token,
            token,
            expires=expire,
            path=request.app.admin_path,
            httponly=True,
        )
        await redis.set(constants.LOGIN_USER.format(token=token), admin.pk, ex=expire)
        return response
