import logging

from mongoengine import connect, disconnect
from pymongo import ReadPreference

from ai_mf_backend.utils.v1.errors import MongoConnectionFailException

from ai_mf_backend.config.v1.database_config import mongo_config

logger = logging.getLogger(__name__)


class MongoConnection:
    connection = None

    @classmethod
    def create_connection(cls, **kwargs):
        logger.info("Creating mongo connection")
        if kwargs["MONGO_USERNAME"] and kwargs["MONGO_PASSWORD"]:
            kwargs["MONGODB_CONNECTION"] = (
                f"mongodb://{kwargs['MONGO_USERNAME']}:{kwargs['MONGO_PASSWORD']}@{kwargs['MONGO_HOST']}/{kwargs['MONGO_DB_NAME']}"
            )
        else:
            kwargs["MONGODB_CONNECTION"] = (
                f"mongodb://{kwargs['MONGO_HOST']}/{kwargs['MONGO_DB_NAME']}"
            )
        if "READ_SECONDARY" in kwargs and kwargs["READ_SECONDARY"] is True:
            logger.info("Mongo: Using Read preference: Secondary")
            cls.connection = connect(
                mongo_config.MONGO_DB_NAME,
                host=f"{kwargs['MONGODB_CONNECTION']}?retryWrites=true&w=majority&authSource=admin",
                read_preference=ReadPreference.SECONDARY,
                alias="default",
            )
        else:
            logger.info("Mongo: Using Read preference: Primary")
            cls.connection = connect(
                mongo_config.MONGO_DB_NAME,
                host=f"{kwargs['MONGODB_CONNECTION']}?retryWrites=true&w=majority&authSource=admin",
                alias="default",
            )
        logger.info("Mongo connection created")

    @classmethod
    def db_disconnection(cls):
        # https://docs.mongoengine.org/guide/connecting.html#disconnecting-an-existing-connection
        # mongoengine creates a global connection
        # so disconnect should be used from library not the created object
        disconnect()
        logger.info("Mongo connection disconnected")

    @classmethod
    def check_connection(cls):
        if cls.connection.client.command("ping")["ok"]:
            logger.info("Mongo Ping Successfull")
        else:
            raise MongoConnectionFailException(f"Unable to connect to Mongo")
