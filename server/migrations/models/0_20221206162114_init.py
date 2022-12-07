from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `task` (
    `task_id` VARCHAR(255) NOT NULL  PRIMARY KEY,
    `md5` VARCHAR(255) NOT NULL  COMMENT 'md5值',
    `status` INT NOT NULL  DEFAULT 0
) CHARACTER SET utf8mb4 COMMENT='任务';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
