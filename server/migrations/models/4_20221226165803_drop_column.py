from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `uknow` MODIFY COLUMN `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间';
        ALTER TABLE `uknow` MODIFY COLUMN `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `uknow` MODIFY COLUMN `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6);
        ALTER TABLE `uknow` MODIFY COLUMN `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6);"""
