from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `icem_hardware` MODIFY COLUMN `cpu_model` VARCHAR(255) NOT NULL  COMMENT 'CPU型号';
        ALTER TABLE `icem_hardware` MODIFY COLUMN `cpu_model` VARCHAR(255) NOT NULL  COMMENT 'CPU型号';
        ALTER TABLE `icem_hardware` MODIFY COLUMN `cpu_model` VARCHAR(255) NOT NULL  COMMENT 'CPU型号';
        ALTER TABLE `icem_hardware` MODIFY COLUMN `cpu_model` VARCHAR(255) NOT NULL  COMMENT 'CPU型号';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `icem_hardware` MODIFY COLUMN `cpu_model` DOUBLE NOT NULL  COMMENT 'CPU型号';
        ALTER TABLE `icem_hardware` MODIFY COLUMN `cpu_model` DOUBLE NOT NULL  COMMENT 'CPU型号';
        ALTER TABLE `icem_hardware` MODIFY COLUMN `cpu_model` DOUBLE NOT NULL  COMMENT 'CPU型号';
        ALTER TABLE `icem_hardware` MODIFY COLUMN `cpu_model` DOUBLE NOT NULL  COMMENT 'CPU型号';"""
