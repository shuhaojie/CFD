from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `uknow` ADD `order_id` VARCHAR(255) NOT NULL  COMMENT '订单id';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `uknow` DROP COLUMN `order_id`;"""
