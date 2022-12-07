# -*- coding: utf-8 -*-
"""
# @File    : single_app.py
# @Time    : 2020/5/21 10:16 上午
"""

import fcntl
import os
import sys
import tempfile


class SingleInstanceException(Exception):
    pass


class SingleInstance(object):
    """
    SingleInstance 用于确保你的代码同一时间只能有一个实例运行

    使用方法：
    me = SingleInstance('scheduler@1dea12c1-5539-4985-aab6-c0897c0f17a6')

    process_uid 应确保是全局唯一uuid
    """

    def __init__(self, process_uid):
        self.initialized = False
        self.lockfile = os.path.normpath(
            tempfile.gettempdir() + '/' + f'{process_uid}.lock')

        self.fp = open(self.lockfile, 'w')
        self.fp.flush()

        try:
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise SingleInstanceException(
                "Another instance is already running, exiting!")

        self.initialized = True

    def __del__(self):
        if not self.initialized:
            return

        try:
            fcntl.lockf(self.fp, fcntl.LOCK_UN)
            if os.path.isfile(self.lockfile):
                os.unlink(self.lockfile)
        except Exception as e:
            sys.exit(-1)


if __name__ == "__main__":
    si = SingleInstance('scheduler@1dea12c1-5539-4985-aab6-c0897c0f17a6')
