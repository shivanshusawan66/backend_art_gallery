import logging

from ai_mf_backend.config.v1.database_config import mongo_config
from ai_mf_backend.utils.v1.database.mongo import MongoConnection

logger = logging.getLogger(__name__)


def create_connections():
    logger.info("Creating connections")
    _ = MongoConnection.create_connection(
        MONGO_DB_NAME=mongo_config.MONGO_DB_NAME,
        MONGO_HOST=mongo_config.MONGO_HOST,
        MONGO_USERNAME=mongo_config.MONGO_USERNAME,
        MONGO_PASSWORD=mongo_config.MONGO_PASSWORD,
        READ_SECONDARY=mongo_config.READ_SECONDARY,
    )


def remove_connections():
    MongoConnection.db_disconnection()


def check_connections():
    logger.info("Checking connections")
    MongoConnection.check_connection()


logger.info("Creating connections.")
create_connections()
