import io
import logging
import os
from contextlib import contextmanager
from functools import lru_cache
from io import StringIO
from typing import Optional

from dotenv.main import DotEnv
from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)


def my_get_stream(self):
    """重写python-dotenv读取文件的方法，使用utf-8，支持读取包含中文的.env配置文件"""
    if isinstance(self.dotenv_path, StringIO):
        yield self.dotenv_path
    elif os.path.isfile(self.dotenv_path):
        with io.open(self.dotenv_path, encoding='utf-8') as stream:
            yield stream
    else:
        if self.verbose:
            logger.warning("File doesn't exist %s", self.dotenv_path)
        yield StringIO('')


DotEnv._get_stream = contextmanager(my_get_stream)


class Settings(BaseSettings):
    """System configurations."""

    # 系统环境  默认开发
    ENVIRONMENT: Optional[str] = Field(None, env="ENVIRONMENT")

    # 系统安全秘钥
    SECRET_KEY = 'ZEuk2U9svM3WRJql4Fs2lEvD05ZDQXZdKboim__SQqsUUqJwStZJq6u0e30bIL4Qe80PB48X1dcIZHjxqLzUiA'

    # API版本号
    API_V1_STR = ""

    # token过期时间
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8

    # 算法
    ALGORITHM = "HS256"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 加载.env文件的配置
    class Config:
        # 加载一下环境文件 手动设置的环境变量>.env中设置的环境变
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


# 加载一下环境文件 手动设置的环境变量
class Config(Settings):
    """Development configurations."""

    # Mysql
    MYSQL_SERVER: Optional[str] = Field(None, env="MYSQL_SERVER")
    MYSQL_USER: Optional[str] = Field(None, env="MYSQL_USER")
    MYSQL_PASSWORD: Optional[str] = Field(None, env="MYSQL_PASSWORD")
    MYSQL_PORT: Optional[int] = Field(None, env="MYSQL_PORT")
    MYSQL_DB: Optional[str] = Field(None, env="MYSQL_DB")

    # cfd监控路径
    MONITOR_PATH: Optional[str] = Field(None, env="MONITOR_PATH")
    PREPARE_PATH: Optional[str] = Field(None, env="PREPARE_PATH")
    ARCHIVE_PATH: Optional[str] = Field(None, env="ARCHIVE_PATH")
    FILE_DIFF_TIME: Optional[str] = Field(None, env="FILE_DIFF_TIME")

    # MINIO配置
    MINIO_BUCKET: Optional[str] = Field(None, env="MINIO_BUCKET")
    MINIO_END: Optional[str] = Field(None, env="MINIO_END")
    MINIO_PORT: Optional[str] = Field(None, env="MINIO_PORT")
    MINIO_USER: Optional[str] = Field(None, env="MINIO_USER")
    MINIO_PASSWD: Optional[str] = Field(None, env="MINIO_PASSWD")

    # REDIS配置
    REDIS_HOST: Optional[str] = Field(None, env="REDIS_HOST")
    REDIS_USER: Optional[str] = Field(None, env="REDIS_USER")
    REDIS_MASTER_NAME: Optional[str] = Field(None, env="REDIS_MASTER_NAME")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    REDIS_SENTRY: Optional[str] = Field(None, env="REDIS_SENTRY")

    # 第三方url
    BASE_URL: Optional[str] = Field(None, env="BASE_URL")


@lru_cache()  # 结果缓存 仅启动时运行一次
def get_configs():
    """
    返回当前环境配置 settings
    """
    return Config()


configs = get_configs()
