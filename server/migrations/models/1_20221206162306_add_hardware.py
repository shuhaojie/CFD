from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `task` ADD `hardware` VARCHAR(255) NOT NULL  COMMENT '硬件配置';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `task` DROP COLUMN `hardware`;"""
