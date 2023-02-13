# v1.1.0部署

## 1. 安装软件

软件清单

```bash
1. python 3.10
2. redis
3. mysql
```

## 2. 安装python包

`pip install -r requirements.txt`

## 3. 数据库建表

原始SQL
```sql
CREATE TABLE IF NOT EXISTS `admin` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(200) NOT NULL,
    `last_login` DATETIME(6) NOT NULL  COMMENT 'Last Login',
    `email` VARCHAR(200) NOT NULL  DEFAULT '',
    `avatar` VARCHAR(200) NOT NULL  DEFAULT '',
    `intro` LONGTEXT NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `archive` (
    `uuid` VARCHAR(255) NOT NULL  PRIMARY KEY DEFAULT '0701d147-85cd-11ed-a75a-e0d045dbb4d7',
    `task_id` VARCHAR(255) NOT NULL  COMMENT '任务id',
    `task_type` VARCHAR(255) NOT NULL  COMMENT '任务类别',
    `task_status` VARCHAR(255) NOT NULL  COMMENT '任务状态'
) CHARACTER SET utf8mb4 COMMENT='任务归档表';
CREATE TABLE IF NOT EXISTS `fluent_hardware` (
    `level` VARCHAR(255) NOT NULL  PRIMARY KEY COMMENT '硬件配置等级',
    `fs_instance_type` VARCHAR(255) NOT NULL  COMMENT '速石实例类型',
    `process_num` INT NOT NULL  COMMENT 'fluent进程数' DEFAULT 28,
    `enum` VARCHAR(255) NOT NULL  COMMENT 'fluent求解器' DEFAULT '3dpp',
    `cpu_frequency` DOUBLE NOT NULL  COMMENT 'CPU核心频率',
    `cpu_model` DOUBLE NOT NULL  COMMENT 'CPU型号',
    `v_cpu` INT NOT NULL  COMMENT '虚拟CPU数',
    `memory` INT NOT NULL  COMMENT '显存数',
    `price` DOUBLE NOT NULL  COMMENT '价格(元/小时)',
    `system_platform` VARCHAR(255) NOT NULL  COMMENT '操作系统类型'
) CHARACTER SET utf8mb4 COMMENT='Fluent硬件配置表';
CREATE TABLE IF NOT EXISTS `fluent_prof` (
    `prof_name` VARCHAR(255) NOT NULL  PRIMARY KEY COMMENT 'prof文件名称',
    `prof_path` VARCHAR(255) NOT NULL  COMMENT 'prof文件路径'
) CHARACTER SET utf8mb4 COMMENT='fluent prof文件对应表';
CREATE TABLE IF NOT EXISTS `fluent_task` (
    `uuid` VARCHAR(255) NOT NULL  PRIMARY KEY DEFAULT '0701d147-85cd-11ed-a75a-e0d045dbb4d7',
    `task_id` VARCHAR(255) NOT NULL  COMMENT '任务id',
    `task_status` VARCHAR(255)   COMMENT '任务状态',
    `fluent_md5` VARCHAR(255)   COMMENT 'fluent md5值',
    `await_number` INT   COMMENT '排队编号',
    `job_id` VARCHAR(255)   COMMENT '速石返回的job_id'
) CHARACTER SET utf8mb4 COMMENT='Fluent任务表';
CREATE TABLE IF NOT EXISTS `icem_hardware` (
    `level` VARCHAR(255) NOT NULL  PRIMARY KEY COMMENT '硬件配置等级',
    `fs_instance_type` VARCHAR(255) NOT NULL  COMMENT '速石实例类型',
    `cpu_frequency` DOUBLE NOT NULL  COMMENT 'CPU核心频率',
    `cpu_model` DOUBLE NOT NULL  COMMENT 'CPU型号',
    `v_cpu` INT NOT NULL  COMMENT '虚拟CPU数',
    `memory` INT NOT NULL  COMMENT '显存数',
    `price` DOUBLE NOT NULL  COMMENT '价格(元/小时)',
    `system_platform` VARCHAR(255) NOT NULL  COMMENT '操作系统类型'
) CHARACTER SET utf8mb4 COMMENT='Icem硬件配置表';
CREATE TABLE IF NOT EXISTS `icem_task` (
    `uuid` VARCHAR(255) NOT NULL  PRIMARY KEY DEFAULT '0701d147-85cd-11ed-a75a-e0d045dbb4d7',
    `task_id` VARCHAR(255) NOT NULL  COMMENT '任务id',
    `task_status` VARCHAR(255)   COMMENT '任务状态',
    `icem_md5` VARCHAR(255)   COMMENT 'icem md5值',
    `await_number` INT   COMMENT '排队编号',
    `job_id` INT   COMMENT '速石返回的job_id'
) CHARACTER SET utf8mb4 COMMENT='Icem任务表';
CREATE TABLE IF NOT EXISTS `token` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `access_token` VARCHAR(1024) NOT NULL  COMMENT '文件md5值',
    `expire_time` DATETIME(6) NOT NULL  COMMENT 'token过期时间'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `uknow` (
    `uuid` VARCHAR(255) NOT NULL  PRIMARY KEY DEFAULT '0701d147-85cd-11ed-a75a-e0d045dbb4d7',
    `task_id` VARCHAR(255) NOT NULL  COMMENT '任务id',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `task_name` VARCHAR(255)   COMMENT '任务名称',
    `username` VARCHAR(255)   COMMENT '用户名',
    `mac_address` VARCHAR(255) NOT NULL  COMMENT 'MAC地址',
    `md5` VARCHAR(255) NOT NULL  COMMENT '文件md5值',
    `icem_hardware_level` VARCHAR(255) NOT NULL  COMMENT 'Icem硬件配置等级',
    `icem_params` LONGTEXT   COMMENT 'Icem参数',
    `fluent_hardware_level` VARCHAR(255) NOT NULL  COMMENT 'Fluent硬件配置等级',
    `fluent_params` LONGTEXT   COMMENT 'Fluent参数',
    `task_queue` INT   COMMENT '任务排队号',
    `data_status` VARCHAR(255)   COMMENT '数据上传状态',
    `data_code` VARCHAR(255)   COMMENT '数据上传状态码',
    `icem_status` VARCHAR(255)   COMMENT 'Icem任务执行状态',
    `icem_queue_number` INT   COMMENT 'Icem排队号',
    `icem_log_file_path` VARCHAR(1024)   COMMENT 'icem日志文件路径',
    `icem_result_file_path` VARCHAR(1024)   COMMENT 'icem结果路径',
    `icem_start` DATETIME(6)   COMMENT 'Icem开始时间',
    `icem_end` DATETIME(6)   COMMENT 'Icem结束时间',
    `icem_duration` DOUBLE   COMMENT 'Icem任务执行时间(秒)',
    `icem_widgets` DOUBLE   COMMENT 'Icem任务花费(RMB/元)',
    `fluent_status` VARCHAR(255)   COMMENT 'Fluent任务执行状态',
    `fluent_queue_number` INT   COMMENT 'Fluent排队号',
    `fluent_log_file_path` VARCHAR(1024)   COMMENT 'fluent日志文件',
    `fluent_result_file_path` VARCHAR(1024)   COMMENT 'fluent结果路径',
    `fluent_start` DATETIME(6)   COMMENT 'Fluent开始时间',
    `fluent_end` DATETIME(6)   COMMENT 'Fluent结束时间',
    `fluent_duration` DOUBLE   COMMENT 'Fluent任务执行时间(秒)',
    `fluent_widgets` DOUBLE   COMMENT 'Fluent任务花费(RMB/元'
) CHARACTER SET utf8mb4 COMMENT='uknow交互表';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
```

v1.1.0更新
```sql
ALTER TABLE `uknow` ADD `order_id` VARCHAR(255) NOT NULL  COMMENT '订单id';
```

## 4. 入库`FluentProf`和`Admin`表

```bash
cd server
python scripts/add.py
```

## 5. 环境变量

v1.1.0新增ADMIN_EMAIL

ENVIRONMENT对应修改, 测试环境为testing, 研发环境为production

## 6. 白名单

研发环境: http://172.16.1.37:31226

测试环境: http://testservices.unionstrongtech.com

正式环境: http://services.unionstrongtech.com

## 6. 启动服务

### 1. 启动fastapi

```bash
cd server
python main.py
```

### 2. 启动celery

`bash start.sh`


