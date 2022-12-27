from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `token` MODIFY COLUMN `access_token` VARCHAR(1024) NOT NULL  COMMENT '文件md5值';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `token` MODIFY COLUMN `access_token` VARCHAR(255) NOT NULL  COMMENT '文件md5值';"""
