from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `uknow` MODIFY COLUMN `icem_result_file_path` VARCHAR(1024)   COMMENT 'icem结果路径';
        ALTER TABLE `uknow` MODIFY COLUMN `fluent_result_file_path` VARCHAR(1024)   COMMENT 'fluent结果路径';
        ALTER TABLE `uknow` MODIFY COLUMN `fluent_log_file_path` VARCHAR(1024)   COMMENT 'fluent日志文件';
        ALTER TABLE `uknow` MODIFY COLUMN `icem_log_file_path` VARCHAR(1024)   COMMENT 'icem日志文件路径';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `uknow` MODIFY COLUMN `icem_result_file_path` VARCHAR(255)   COMMENT 'icem结果路径';
        ALTER TABLE `uknow` MODIFY COLUMN `fluent_result_file_path` VARCHAR(255)   COMMENT 'fluent结果路径';
        ALTER TABLE `uknow` MODIFY COLUMN `fluent_log_file_path` VARCHAR(255)   COMMENT 'fluent日志文件';
        ALTER TABLE `uknow` MODIFY COLUMN `icem_log_file_path` VARCHAR(255)   COMMENT 'icem日志文件路径';"""
