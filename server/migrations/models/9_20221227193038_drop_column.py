from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `fluent_hardware` RENAME COLUMN `level` TO `id`;
        ALTER TABLE `fluent_hardware` ADD `level` VARCHAR(255) NOT NULL  COMMENT '硬件配置等级';
        ALTER TABLE `icem_hardware` RENAME COLUMN `level` TO `id`;
        ALTER TABLE `icem_hardware` ADD `level` VARCHAR(255) NOT NULL  COMMENT '硬件配置等级';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `icem_hardware` RENAME COLUMN `id` TO `level`;
        ALTER TABLE `icem_hardware` DROP COLUMN `level`;
        ALTER TABLE `fluent_hardware` RENAME COLUMN `id` TO `level`;
        ALTER TABLE `fluent_hardware` DROP COLUMN `level`;"""
