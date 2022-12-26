import datetime
from tortoise import fields
from tortoise.models import Model
from utils.constant import MyConstant
from commons.base_model import AbstractBaseModel
from fastapi_admin.models import AbstractAdmin


# CFD和Uknow用户进行交互, 返给用户想要的信息. 这个表会注册到admin页面中
class Uknow(AbstractBaseModel):
    task_id = fields.CharField(max_length=MyConstant.MAX_LENGTH, description='任务id')
    create_time = fields.DatetimeField(description='创建时间', null=True)
    task_name = fields.CharField(description='任务名称', max_length=MyConstant.MAX_LENGTH, null=True)
    username = fields.CharField(description="用户名", max_length=MyConstant.MAX_LENGTH, null=True)
    mac_address = fields.CharField(description="MAC地址", max_length=MyConstant.MAX_LENGTH)
    md5 = fields.CharField(description="文件md5值", max_length=MyConstant.MAX_LENGTH)

    # 跑Icem任务的硬件配置
    icem_hardware_level = fields.CharField(description="Icem硬件配置等级", max_length=MyConstant.MAX_LENGTH)
    # 跑 Icem bash的时候需要的参数, 提供给bash脚本, send_config会给过来
    icem_params = fields.TextField(description="Icem参数", null=True)
    # GEO_EXTRACT_CURVES = fields.FloatField()
    # GEO_SET_FAMILY_PARAMS = fields.FloatField()

    # 跑Fluent任务的硬件配置
    fluent_hardware_level = fields.CharField(description="Fluent硬件配置等级", max_length=MyConstant.MAX_LENGTH)
    # 跑Fluent bash的时候额外需要的参数, 提供给bash脚本
    fluent_params = fields.TextField(description="Fluent参数", null=True)
    # prof_number = fields.IntField(description="prof文件编号")

    # 任务整体排队号
    task_queue = fields.IntField(description="任务排队号", null=True)
    # 共三种: pending, success, fail(此时会告诉原因,主要是md5校验没有通过, 可能用户上传一半关机了)
    data_status = fields.CharField(description="数据上传状态",
                                   max_length=MyConstant.MAX_LENGTH,
                                   null=True)
    # 当数据上传失败的时候, 告诉用户失败原因, 主要是md5校验没有通过
    data_code = fields.CharField(description="数据上传状态码",
                                 max_length=MyConstant.MAX_LENGTH,
                                 null=True)

    # 共五种: queue, schedule, pending, success, fail
    icem_status = fields.CharField(description="Icem任务执行状态",
                                   max_length=MyConstant.MAX_LENGTH,
                                   null=True)
    # 如果是排队中的话, 需要有一个排队号
    icem_queue_number = fields.IntField(description="Icem排队号", null=True)
    # 执行错误的时候, 需要有一个日志文件, 下载下来之后需要重命名
    icem_log_file_path = fields.CharField(max_length=1024,
                                          description="icem日志文件路径",
                                          null=True)
    icem_result_file_path = fields.CharField(max_length=1024,
                                             description="icem结果路径",
                                             null=True)
    icem_start = fields.DatetimeField(description='Icem开始时间', null=True)
    icem_end = fields.DatetimeField(description='Icem结束时间', null=True)
    icem_duration = fields.FloatField(description="Icem任务执行时间(秒)", null=True)
    icem_widgets = fields.FloatField(description="Icem任务花费(RMB/元)", null=True)

    # 共五种: queue, schedule, pending, success, fail
    fluent_status = fields.CharField(description="Fluent任务执行状态",
                                     max_length=MyConstant.MAX_LENGTH,
                                     null=True)
    # 如果是排队中的话, 需要有一个排队号
    fluent_queue_number = fields.IntField(description="Fluent排队号", null=True)
    # 执行错误的时候, 需要有一个日志文件, 下载下来之后需要重命名
    fluent_log_file_path = fields.CharField(max_length=1024,
                                            description="fluent日志文件",
                                            null=True)
    fluent_result_file_path = fields.CharField(max_length=1024,
                                               description="fluent结果路径",
                                               null=True)
    fluent_start = fields.DatetimeField(description='Fluent开始时间', null=True)
    fluent_end = fields.DatetimeField(description='Fluent结束时间', null=True)
    fluent_duration = fields.FloatField(description="Fluent任务执行时间(秒)", null=True)
    fluent_widgets = fields.FloatField(description="Fluent任务花费(RMB/元", null=True)

    class Meta:
        table = "uknow"
        table_description = "uknow交互表"


# CFD和速石进行交互, 发送跑Icem任务时, 速石想要的信息, 以及可以从速石拿到的有用信息
class IcemTask(AbstractBaseModel):
    task_id = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                               description='任务id')
    # 共六种: queue, pending, schedule, dealing, success, fail
    task_status = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                                   description='任务状态',
                                   null=True)
    # 给速石做校验
    icem_md5 = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                                description='icem md5值',
                                null=True)
    await_number = fields.IntField(description="排队编号", null=True)
    job_id = fields.IntField(max_length=MyConstant.MAX_LENGTH,
                             description='速石返回的job_id',
                             null=True)

    class Meta:
        table = "icem_task"
        table_description = "Icem任务表"


class FluentTask(AbstractBaseModel):
    task_id = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                               description='任务id')
    task_status = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                                   description='任务状态',
                                   null=True)
    # 给速石做校验
    fluent_md5 = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                                  description='fluent md5值',
                                  null=True)
    await_number = fields.IntField(description="排队编号", null=True)
    job_id = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                              description='速石返回的job_id',
                              null=True)

    class Meta:
        table = "fluent_task"
        table_description = "Fluent任务表"


# 作用是减少FluentTask和IcemTask数据量, 一方面是更好的排队, 另外一方面是查状态的时候比较方便
class Archive(AbstractBaseModel):
    task_id = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                               description='任务id')
    # Icem或者Fluent
    task_type = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                                 description='任务类别')
    task_status = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                                   description='任务状态')

    class Meta:
        table = "archive"
        table_description = "任务归档表"


class IcemHardware(Model):
    # 共三种: low, medium, high
    level = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                             description='硬件配置等级',
                             pk=True)
    fs_instance_type = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                                        description='速石实例类型')
    cpu_frequency = fields.FloatField(description='CPU核心频率')
    cpu_model = fields.FloatField(description='CPU型号')
    v_cpu = fields.IntField(description='虚拟CPU数')
    memory = fields.IntField(description='显存数')
    price = fields.FloatField(description='价格(元/小时)')
    system_platform = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                                       description='操作系统类型')

    class Meta:
        table = "icem_hardware"
        table_description = "Icem硬件配置表"


class FluentHardware(Model):
    # 共三种: low, medium, high
    level = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                             description='硬件配置等级',
                             pk=True)

    fs_instance_type = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                                        description='速石实例类型')
    process_num = fields.IntField(description='fluent进程数', default=28)
    enum = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                            description='fluent求解器',
                            default='3dpp')
    cpu_frequency = fields.FloatField(description='CPU核心频率')
    cpu_model = fields.FloatField(description='CPU型号')
    v_cpu = fields.IntField(description='虚拟CPU数')
    memory = fields.IntField(description='显存数')
    price = fields.FloatField(description='价格(元/小时)')
    system_platform = fields.CharField(max_length=MyConstant.MAX_LENGTH,
                                       description='操作系统类型')

    class Meta:
        table = "fluent_hardware"
        table_description = "Fluent硬件配置表"


# Fluent脚本中prof文件对应表
class FluentProf(Model):
    prof_name = fields.CharField(description="prof文件名称", pk=True, max_length=MyConstant.MAX_LENGTH)
    prof_path = fields.CharField(description="prof文件路径", max_length=MyConstant.MAX_LENGTH)

    class Meta:
        table = "fluent_prof"
        table_description = "fluent prof文件对应表"


class Token(Model):
    access_token = fields.CharField(description="文件md5值", max_length=1024)
    expire_time = fields.DatetimeField(description='token过期时间')


class Admin(AbstractAdmin):
    last_login = fields.DatetimeField(description="Last Login", default=datetime.datetime.now)
    email = fields.CharField(max_length=200, default="")
    avatar = fields.CharField(max_length=200, default="")
    intro = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}#{self.username}"
