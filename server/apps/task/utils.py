import os
import traceback

import pytz
import requests
import base64
import json
import pickle
import shutil
import time
import zipfile
import re
import sys
import yaml
import hashlib
import asyncio
from glob import glob
from datetime import datetime, timedelta
import smtplib
from pathlib import Path
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from logs import api_log
from config import configs
from utils.oss import Minio
from utils.constant import BUSINESS, Status
from apps.models import Token, Uknow, IcemHardware, FluentHardware
from tortoise import Tortoise
from dbs.database import TORTOISE_ORM, database_init

minio = Minio()


class FileTool:
    """
    读/写 json文件
    读/写 yaml文件
    删除/创建 目录
    删除/复制 文件
    压缩/解压 文件
    移动 目录/文件
    """

    @classmethod
    def check_path(cls, path):
        illegal_paths = ["null", "none", "None", "./", "../"]
        assert not re.search(r"\s", path), " /t/n/r existed"
        assert path != "/", "/ is dangerous"
        return all(i not in path for i in illegal_paths)

    @classmethod
    def read_json(cls, file, default=None, encoding=None):
        if default is None:
            default = {}
        try:
            with open(file, "r", encoding=encoding) as infile:
                return json.load(infile)
        except Exception as e:
            api_log.warning(
                "error reading json: {}, using {}".format(e, default))
            return default

    @classmethod
    def write_json(cls, to_file, data):
        with open(to_file, "w") as f:
            json.dump(data, f)

    @classmethod
    def write_json_v2(cls, to_file, data):
        with open(to_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)

    @classmethod
    def delete_directory(cls, directory, verbose=False):
        if os.path.isdir(directory):
            shutil.rmtree(directory)
            if verbose:
                api_log.info(f"removed directory: {directory}")

    @classmethod
    def recursion_del_null_directory(cls, base_path):
        # 递归删除空文件夹
        for root, dirs, filenames in os.walk(base_path):
            if os.path.isdir(root):
                try:
                    os.removedirs(root)
                    api_log.info(f"removed null directory: {root}")
                except:
                    pass

    @classmethod
    def make_directory(cls, directory, delete=False, exist_ok=True):
        if delete:
            cls.delete_directory(directory)
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=exist_ok)
        return os.path.abspath(directory)

    @classmethod
    def delete_file(cls, file, verbose=False):
        # 检查文件名规范
        assert cls.check_path(file)
        if os.path.isfile(file):
            try:
                os.remove(file)
            except Exception as e:
                api_log.exception(e)

            if verbose:
                api_log.info(f"removed file: {file}")

    @classmethod
    def delete_files(cls, files, verbose=False):
        for file in files:
            if os.path.isfile(file):
                try:
                    os.remove(file)
                except Exception as e:
                    api_log.exception(e)

                if verbose:
                    api_log.info(f"removed file: {file}")

    @classmethod
    def copy_file(cls, from_file, to_file, exist_ok=True):
        if os.path.isfile(from_file):
            if not os.path.isdir(os.path.dirname(to_file)):
                os.makedirs(os.path.dirname(to_file), exist_ok=exist_ok)
            shutil.copyfile(from_file, to_file)
        return from_file

    @classmethod
    def copy_file_v2(cls, from_folder, to_folder):
        # 将一个文件夹下的所有文件递归拷贝到另外一个文件夹下
        if not os.path.exists(to_folder):  # 如不存在目标目录则创建
            os.makedirs(to_folder)
        file_list = os.listdir(from_folder)
        for f in file_list:
            file_path = os.path.join(from_folder, f)
            if os.path.isdir(file_path):
                cls.copy_file_v2(file_path,
                                 os.path.join(to_folder, f))
            else:
                shutil.copy(file_path, to_folder)

    @classmethod
    def move_folder(cls, from_folder, to_folder, exist_ok=True):
        if os.path.isdir(from_folder):
            if not os.path.isdir(os.path.dirname(to_folder)):
                os.makedirs(os.path.dirname(to_folder), exist_ok=exist_ok)
            shutil.move(from_folder, to_folder)

    @classmethod
    def move_files(cls, from_folder, to_folder):
        new_paths = []
        for f in os.listdir(from_folder):
            file_path = os.path.join(to_folder, f)
            shutil.move(os.path.join(from_folder, f), file_path)
            new_paths.append(file_path)
        return new_paths

    @classmethod
    def files_in_folder(cls, folder):
        return [os.path.join(folder, n) for n in os.listdir(folder) if os.path.isfile(os.path.join(folder, n))]

    @classmethod
    def folders_in_folder(cls, folder):
        return [os.path.join(folder, n) for n in os.listdir(folder) if os.path.isdir(os.path.join(folder, n))]

    @classmethod
    def unzip_file(cls, file, dest):
        file_zip = zipfile.ZipFile(file)
        file_zip.extractall(dest)
        file_zip.close()
        return dest

    @classmethod
    def zip_folder(cls, folder, dest):
        """
        folder: 要解压的文件夹名
        dest: 目标文件
        """
        zipf = zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(folder):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.join(os.path.relpath(root, folder), file),
                )
        zipf.close()
        return dest

    @staticmethod
    def make_zipfile(output_filename, source_dir):
        relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename):  # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

    @classmethod
    def read_file(cls, filepath, mode="r"):
        f = open(filepath, mode)
        content = f.read()
        f.close()
        return content

    @classmethod
    def write_file(cls, save_path, b64_str, mode='w'):
        try:
            with open(save_path, mode) as f:
                f.write(b64_str)
            return True
        except Exception as e:
            api_log.exception(e)
            return False

    @classmethod
    def read_yaml(cls, file, default=None, err_msg=None):
        if default is None:
            default = {}
        try:
            with open(file, "r") as f:
                return yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            if err_msg is not None:
                api_log.warning(err_msg)
            else:
                api_log.warning(
                    "error reading yaml: {}, using {}".format(e, default))
            return default

    @classmethod
    def write_yaml(cls, file, data, **kwds):
        with open(file, "w") as outfile:
            yaml.dump(data, outfile, **kwds)

    @classmethod
    def write_pkl(cls, filepath, data):
        with open(filepath, "wb") as f:
            pickle.dump(data, f)

    @classmethod
    def read_pkl(cls, filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)

    @classmethod
    def get_all_files(cls, folder):
        result = [y for x in os.walk(folder)
                  for y in glob(os.path.join(x[0], '*.dcm'))]
        return result

    @classmethod
    def get_dirs(cls, folder):
        # 获取当前文件夹子文件夹（不递归）
        if os.listdir(folder):
            return os.listdir(folder)
        else:
            return []

    @classmethod
    def get_size(cls, start_path='.'):
        total_size = 0
        for dirpath, _, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        return total_size

    @classmethod
    def is_write_disk(cls, filename):
        # 文件是否写入磁盘
        if os.path.isfile(filename):
            statbuf = os.stat(filename)  # 文件数据信息, 包含文件修改时间等...
        else:
            return False
        now_time = time.time()
        diff_time = now_time - statbuf.st_mtime
        if diff_time > 10:  # 当前时间和文件修改时间的差值
            return True
        else:
            return False

    @classmethod
    def write_complete(cls, filename):
        is_file_complete = False
        while not is_file_complete:
            is_write_disk = FileTool.is_write_disk(filename)
            if is_write_disk:
                is_file_complete = True
            else:
                time.sleep(3)

    @classmethod
    def get_md5(cls, filename):
        with open(filename, "rb") as f1:
            current_bytes = f1.read()
            a_hash = hashlib.md5(current_bytes).hexdigest()
            return a_hash


def delete_folder(task_id):
    prepare_folder = os.path.join(configs.PREPARE_PATH, task_id)
    monitor_folder = os.path.join(configs.MONITOR_PATH, task_id)
    monitor_zip = os.path.join(configs.MONITOR_PATH, task_id+'.zip')
    archive_folder = os.path.join(configs.ARCHIVE_PATH, task_id)
    if os.path.exists(prepare_folder):
        shutil.rmtree(prepare_folder)
    if os.path.exists(monitor_folder):
        shutil.rmtree(monitor_folder)
    if os.path.exists(monitor_zip):
        os.remove(monitor_zip)
    if os.path.exists(archive_folder):
        shutil.rmtree(archive_folder)


def generate_token():
    base_url = "http://120.48.150.243/api/v1/auth/signin"
    password = 'fs@2022!'
    encoded_password = str(base64.b64encode(password.encode('utf-8')), 'utf-8')
    params = {'usernameOrEmail': 'admin', 'encodedPassword': encoded_password}
    r = requests.post(base_url, json=params)
    token = r.json()['accessToken']
    return token


async def get_token():
    # 判断token是否存在
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await database_init()
    query = await Token.filter().first()
    await Tortoise.close_connections()
    if query:
        # 如果存在, 先判断token是否过期
        expire_time = query.expire_time
        now = datetime.now().replace(tzinfo=pytz.timezone('UTC'))
        # 如果沒有过期，从数据库中获取token
        if expire_time > now:
            token = query.access_token
            return token
        # 如果过期，需要重新获取一次token
        else:
            token = generate_token()
            # 获得完token之后，更新一下数据库
            expire_time = datetime.now() + timedelta(hours=10)
            await database_init()
            await Token.filter().update(access_token=token, expire_time=expire_time)
            await Tortoise.close_connections()
            return token
    else:
        # token不存在，也需要获取一下token
        token = generate_token()
        # 获得完token之後，将token入库
        expire_time = datetime.now() + timedelta(hours=10)
        await database_init()
        await Token.create(access_token=token, expire_time=expire_time)
        await Tortoise.close_connections()
        return token


def create_remote_folder(task_id, headers):
    json_data = {
        'parent_path': '/usc',
        'name': task_id,
        'storage_id': -1,
    }
    response = requests.post('http://120.48.150.243/fa/api/v0/file/new', headers=headers, json=json_data, verify=False)
    return response


def upload_file(task_id, task_type, headers):
    base_url = "http://120.48.150.243/fa/api/v0/upload/"
    abs_path = os.path.join(configs.PREPARE_PATH, task_id, f"{task_type}.zip")
    files = {
        'file': open(abs_path, 'rb'),
        'key': (None, f'usc/{task_id}/{task_type}.zip'),
        'storage_id': (None, '-1'),
    }

    r = requests.post(
        base_url,
        files=files,
        headers=headers
    )
    return r.json()


def download_file(url, dest_folder, headers):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)
    r = requests.get(url, stream=True, headers=headers)
    if r.ok:
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        return True
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))
        return False


def download_complete(file_path):
    try:
        is_download_complete = False
        while not is_download_complete:
            if os.path.isfile(file_path) and FileTool.is_write_disk(file_path):
                is_download_complete = True
            else:
                await asyncio.sleep(5)
    except Exception as e:
        api_log.error(e)
        f = traceback.format_exc()
        api_log.error(f)


def create_job(task_id, task_type, md5, headers, hardware_level='middle', solver='3ddp', parallel_number=28):
    base_url = 'http://120.48.150.243/api/v1/jobs'
    now = datetime.now()
    task_name = f'{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}_{task_type}_{configs.ENVIRONMENT}'
    if task_type == 'icem':
        # 目前暂时用这个固定配置, 这个是根据用户选择的配置来的
        if hardware_level == 'middle':
            f = open('./static/sushi/icem_b1.c1.32.json', encoding='UTF-8')
        elif hardware_level == 'low':
            f = open('./static/sushi/icem_b1.c1.24.json', encoding='UTF-8')
        else:
            f = open('./static/sushi/icem_b1.c1.48.json', encoding='UTF-8')
        json_data = json.load(f)
        json_data['inputs'][0]['value'] = f'/usc/{task_id}/{task_type}.zip'
        json_data['inputs'][1]['value'] = md5
        json_data['name'] = task_name
        # https://stackoverflow.com/a/22567429/10844937
        r = requests.post(base_url, json=json_data, headers=headers)
        return r
    else:
        # 目前暂时用这个固定配置, 这个是根据用户选择的配置来的
        if hardware_level == 'middle':
            f = open('./static/sushi/fluent-2019_b1.c1.32.json', encoding='UTF-8')
        elif hardware_level == 'low':
            f = open('./static/sushi/fluent-2019_b1.c1.24.json', encoding='UTF-8')
        else:
            f = open('./static/sushi/fluent-2019_b1.c1.48.json', encoding='UTF-8')
        if hardware_level == 'low':
            parallel_number = 24
        else:
            parallel_number = 28
        json_data = json.load(f)
        json_data['inputs'][0]['value'] = f'/usc/{task_id}/{task_type}.zip'
        json_data['inputs'][1]['value'] = solver
        json_data['inputs'][2]['value'] = parallel_number
        json_data['inputs'][3]['value'] = md5
        json_data['name'] = task_name
        r = requests.post(base_url, json=json_data, headers=headers)
        return r


def reverse_job(job_id, headers):
    base_url = f'http://120.48.150.243/api/v1/jobs/{job_id}'
    r = requests.get(base_url, headers=headers)
    return r.json()


async def task_widget(task_id, task_status='SUCCESS'):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await database_init()
    query = await Uknow.filter(task_id=task_id).first()
    await Tortoise.close_connections()
    icem_start, icem_end, icem_level = query.icem_start, query.icem_end, query.icem_hardware_level
    fluent_start, fluent_end, fluent_level = query.fluent_start, query.fluent_end, query.fluent_hardware_level
    if fluent_start is None:
        fluent_duration = 0
    else:
        fluent_duration = (fluent_end - fluent_start).total_seconds()
    icem_duration = (icem_end - icem_start).total_seconds()
    await database_init()
    icem_query = await IcemHardware.filter(level=icem_level).first()
    await Tortoise.close_connections()
    await database_init()
    fluent_query = await FluentHardware.filter(level=fluent_level).first()
    await Tortoise.close_connections()
    icem_price, fluent_price = icem_query.price, fluent_query.price
    # 存储价格: 时间换算成小时, 乘以单价0.508, 再乘以150G, 除以每个月720个小时
    storage_price = ((icem_duration + fluent_duration) / 3600.0) * 0.508 * 150 / 720
    # 计算价格: 时间*价格
    compute_price = icem_price * icem_duration / 3600.0 + fluent_price * fluent_duration / 3600.0
    # 任务成功, 才需要计算下载价格
    if task_status == 'SUCCESS':
        file_size = os.path.getsize(os.path.join(configs.PREPARE_PATH, task_id, 'fluent_result.zip'))
        # 下载价格: 每GB收费0.8246
        download_price = file_size * 0.8246 / (1024.0 * 1024.0 * 1024.0)
        return round(compute_price + storage_price + download_price, 2)
    else:
        return round(compute_price + storage_price, 2)


def task_fail(task_id, job_id, headers):
    # 取回失败日志
    base_url = f'{configs.SUSHI_URL}/fa/api/v0/download/jobs/job-{job_id}/log/stderr.txt'
    file_path = os.path.join(configs.PREPARE_PATH, task_id)
    is_file_downloaded = download_file(base_url, file_path, headers)
    # 日志文件可能下载失败
    if is_file_downloaded:
        log_file_path = os.path.join(file_path, 'stderr.txt')
        # 日志上传到minio
        minio.upload_file(f'{task_id}/stderr.txt', log_file_path)
        # 文件移动到archive下进行归档
        archive_path = os.path.join(configs.ARCHIVE_PATH, task_id)
        if os.path.isdir(archive_path):
            shutil.rmtree(archive_path)
        shutil.move(file_path, configs.ARCHIVE_PATH)


async def send_mail(task_id, task_status='SUCCESS', job_id=None):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await database_init()
    query = await Uknow.filter(task_id=task_id).first()
    await Tortoise.close_connections()
    order_id = query.order_id
    result = query.fluent_result_file_path
    res = get_user_info(order_id)
    # 如果找不到数据, 就只发admin一个人
    if res['data']:
        send_to = res['data']['email']
        you = f'{configs.ADMIN_EMAIL},{send_to}'
    else:
        you = f'{configs.ADMIN_EMAIL}'
    me = BUSINESS.EMAIL_FROM
    my_password = BUSINESS.EMAIL_PASSWORD

    # 任务耗时
    if query.fluent_end:
        total_seconds = (query.fluent_end - query.create_time).total_seconds()
    else:
        # 如果Icem任务失败, 需要用Icem的时间
        if query.icem_status == Status.FAIL:
            total_seconds = (query.icem_end - query.create_time).total_seconds()
        else:
            if query.create_time:
                total_seconds = ((datetime.now() + timedelta(hours=-8)).replace(
                    tzinfo=pytz.timezone('UTC')) - query.create_time).total_seconds()
            else:
                total_seconds = 0
    m, s = divmod(total_seconds, 60)

    if task_status == 'SUCCESS':
        subject = f'任务{task_id}成功'
        message = f'订单id:{order_id}\n\n任务id:{task_id}\n\n任务耗时:{int(m)}分{int(s)}秒\n\n时间:{str(datetime.now())}'
    elif task_status == 'NETWORK':
        subject = f'任务{task_id}成功'
        message = f'订单id:{order_id}\n\n任务id:{task_id}\n\n时间:{str(datetime.now())}\n\n下载地址:{result}'
    else:
        subject = f'任务{task_id}失败'
        if job_id is not None:
            message = f'订单id:{order_id}\n\n任务id:{task_id}\n\njob_id:{job_id}'
        else:
            message = f'系统错误, 任务id:{task_id}'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = you
    msg.attach(MIMEText(message))
    if task_status == 'SUCCESS':
        file_path = os.path.join(configs.ARCHIVE_PATH, task_id, 'fluent_result.zip')
        part = MIMEBase('application', "octet-stream")
        with open(file_path, 'rb') as file:
            part.set_payload(file.read())

        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename={}'.format(Path(file_path).name))
        msg.attach(part)

    s = smtplib.SMTP_SSL(BUSINESS.EMAIL_HOST)
    s.login(me, my_password)

    s.send_message(msg)
    s.quit()


def get_user_info(order_id):
    request_url = f'{configs.UPIXEL_URL}/api/v1/station/cfd_get_user_info'
    r = requests.get(request_url, params={'order_id': order_id})
    return r.json()


if __name__ == '__main__':
    send_mail('')
