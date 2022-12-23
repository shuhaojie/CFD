#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
文件对象存储模块
@author:温广鑫
@time:2021/05/13
"""
import minio
import traceback
import typing
# 添加配置文件变量
from minio.error import S3Error
from minio.commonconfig import ComposeSource, CopySource
from minio.datatypes import Object
from config import configs
import uuid
import datetime
import time
import os
from multiprocessing import Pool


class Minio:
    """minio服务"""

    def __init__(self):
        self.client = minio.Minio(**{
            'endpoint': f"{configs.MINIO_END}:{configs.MINIO_PORT}",
            'access_key': configs.MINIO_USER,
            'secret_key': configs.MINIO_PASSWD,
            'secure': False
        })

    def upload_stream(self, file_name, data, length):
        """上传文件流,来自request.body"""
        try:
            res = self.client.put_object(bucket_name=configs.MINIO_BUCKET, object_name=file_name,
                                         data=data, length=length)
            return res
        except Exception as exc:
            print(exc)
            return False

    def upload_file(self, file_name, file_path):
        """上传本地文件,来自临时存储"""
        try:
            res = self.client.fput_object(bucket_name=MINIO_BUCKET, object_name=file_name, file_path=file_path)
            return res
        except Exception as exc:
            print(exc)
            return False

    def remove_object(self, file_name):
        """删除文件"""
        try:
            res = self.client.remove_object(bucket_name=MINIO_BUCKET, object_name=file_name)
            return res
        except Exception as exc:
            print(exc)
            return False

    def get_object(self, file_name):
        """下载文件"""
        try:
            res = self.client.get_object(bucket_name=MINIO_BUCKET, object_name=file_name)
            return res
        except Exception as exc:
            print(exc)
            return False

    def exist_object(self, file_name):
        """判断文件是否存在"""
        try:
            res = self.client.stat_object(bucket_name=MINIO_BUCKET, object_name=file_name)
            return True
        except minio.S3Error as exc:
            return False

    def stat_object(self, file_name) -> typing.Union[Object, bool]:
        """文件元信息"""
        try:
            res = self.client.stat_object(bucket_name=MINIO_BUCKET, object_name=file_name)
            return res
        except minio.S3Error as exc:
            return False

    def list_objects(self, prefix):
        """获得前缀目录后的文件列表"""
        objects = self.client.list_objects(bucket_name=MINIO_BUCKET, prefix=prefix)
        _list = []
        for obj in objects:
            _list.append(obj.object_name)
        return _list

    def remove_objects(self, objects):
        """删除批量文件"""
        try:
            for obj in objects:
                self.client.remove_object(bucket_name=MINIO_BUCKET, object_name=obj)
            return True
        except Exception as exc:
            print(exc, traceback.format_exc())
            return False

    def remove_prefix(self, prefix):
        """根据前缀删除文件"""
        try:
            objects = self.list_objects(prefix)
            res = self.remove_objects(objects)
            return res
        except Exception as exc:
            return False

    def copy_object(self, source, target):
        """复制文件
        :param source 来源
        :param target 目标
        """
        copy_source = CopySource(MINIO_BUCKET, source)
        try:
            self.client.copy_object(bucket_name=MINIO_BUCKET, object_name=target,
                                    source=copy_source)
            return True
        except S3Error as err:
            print(err)
            return False

    def compose_objects(self, objects: list, target):
        """合并文件
        :param objects 分块列表
        :param target 合并后目标位置
        """
        sources = [ComposeSource(MINIO_BUCKET, o) for o in objects]
        try:
            res = self.client.compose_object(bucket_name=MINIO_BUCKET, object_name=target, sources=sources)
            return res
        except S3Error as err:
            return False


def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize / float(1024 * 1024)

    return round(fsize, 2)


def upload_file(file_name, file_path):
    """上传本地文件,来自临时存储"""
    oss = Minio()
    try:
        res = oss.client.fput_object(bucket_name=MINIO_BUCKET, object_name=file_name, file_path=file_path)
        return res
    except Exception as exc:
        print(exc)
        return False


def test_minio():
    _path = r"C:\Users\usc\Downloads\test.jpg"
    po = Pool(4)

    for i in range(0, 100):
        _name = f"{i}_{str(uuid.uuid1())}_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')}.jpg"
        f_name = f"test/{_name}"
        po.apply_async(upload_file, (f_name, _path))
    t1 = time.time()
    print(f"----大小----{get_FileSize(_path) * 100}M")
    po.close()  # 关闭进程池，关闭后po不再接收新的请求
    po.join()  # 等待po中所有子进程执行完成，必须放在close语句之后

    print(f"-----用时-----{time.time() - t1}")


if __name__ == '__main__':
    oss = Minio()
    _list = oss.list_objects("('static/dcm/upload/UNDEFINED/originalname/")
    for f in _list:
        target = f.replace("('", "").replace("',)", "")
        print(f, target)
        oss.copy_object(source=f, target=target)
