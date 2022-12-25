from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `admin` ADD `intro` LONGTEXT NOT NULL;
        ALTER TABLE `admin` ADD `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6);
        ALTER TABLE `admin` ADD `email` VARCHAR(200) NOT NULL  DEFAULT '';
        ALTER TABLE `admin` ADD `last_login` DATETIME(6) NOT NULL  COMMENT 'Last Login';
        ALTER TABLE `admin` ADD `avatar` VARCHAR(200) NOT NULL  DEFAULT '';
        ALTER TABLE `admin` MODIFY COLUMN `password` VARCHAR(200) NOT NULL;
        ALTER TABLE `admin` MODIFY COLUMN `password` VARCHAR(200) NOT NULL;
        ALTER TABLE `admin` MODIFY COLUMN `username` VARCHAR(50) NOT NULL;
        ALTER TABLE `admin` MODIFY COLUMN `username` VARCHAR(50) NOT NULL;
        ALTER TABLE `admin` ADD UNIQUE INDEX `uid_admin_usernam_6c25e3` (`username`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `admin` DROP INDEX `idx_admin_usernam_6c25e3`;
        ALTER TABLE `admin` DROP COLUMN `intro`;
        ALTER TABLE `admin` DROP COLUMN `created_at`;
        ALTER TABLE `admin` DROP COLUMN `email`;
        ALTER TABLE `admin` DROP COLUMN `last_login`;
        ALTER TABLE `admin` DROP COLUMN `avatar`;
        ALTER TABLE `admin` MODIFY COLUMN `password` VARCHAR(255) NOT NULL  COMMENT '密码';
        ALTER TABLE `admin` MODIFY COLUMN `password` VARCHAR(255) NOT NULL  COMMENT '密码';
        ALTER TABLE `admin` MODIFY COLUMN `username` VARCHAR(255) NOT NULL  COMMENT '用户名';
        ALTER TABLE `admin` MODIFY COLUMN `username` VARCHAR(255) NOT NULL  COMMENT '用户名';"""
