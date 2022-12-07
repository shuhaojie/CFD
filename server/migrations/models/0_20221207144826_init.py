from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `queue` (
    `task_id` VARCHAR(255) NOT NULL  PRIMARY KEY,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL   COMMENT '是否删除' DEFAULT 0,
    `comment` LONGTEXT   COMMENT '备注'
) CHARACTER SET utf8mb4 COMMENT='排队队列';
CREATE TABLE IF NOT EXISTS `task` (
    `task_id` VARCHAR(255) NOT NULL  PRIMARY KEY,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL   COMMENT '是否删除' DEFAULT 0,
    `comment` LONGTEXT   COMMENT '备注',
    `status` VARCHAR(255) NOT NULL  COMMENT '脚本执行状态' DEFAULT 'pending'
) CHARACTER SET utf8mb4 COMMENT='脚本执行任务';
CREATE TABLE IF NOT EXISTS `uknow` (
    `task_id` VARCHAR(255) NOT NULL  PRIMARY KEY,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL   COMMENT '是否删除' DEFAULT 0,
    `comment` LONGTEXT   COMMENT '备注',
    `status` VARCHAR(255) NOT NULL  COMMENT 'UKnow数据上传状态' DEFAULT 'pending',
    `hardware` VARCHAR(255) NOT NULL  COMMENT '硬件配置',
    `md5` VARCHAR(255) NOT NULL  COMMENT 'md5值'
) CHARACTER SET utf8mb4 COMMENT='Uknow数据上传';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
