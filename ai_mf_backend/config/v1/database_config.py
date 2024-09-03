from typing import Optional

from ai_mf_backend.config.v1 import BaseSettingsWrapper


class MongoConfig(BaseSettingsWrapper):
    """
    Configuration settings for MongoDB database connection.

    :param MONGO_DB_NAME: Name of the mongo database.
    :type MONGO_DB_NAME: str

    :param MONGO_HOST: Hostname of the mongo database.
    :type MONGO_HOST: str

    :param MONGO_USERNAME: Username for mongo authentication, Optional.
    :type MONGO_USERNAME: Optional[str]

    :param MONGO_PASSWORD: Password for mongo authentication, Optional.
    :type MONGO_PASSWORD: Optional[str]

    :param READ_SECONDARY: Boolean to decide whether to read from secondary. Default is 'False'.
    :type READ_SECONDARY: bool

    :returns: This class does not return any values, it merely holds configuration parameters for the MongoDB database.
    """

    MONGO_DB_NAME: str = "ai_mf_backend"
    MONGO_HOST: str
    MONGO_USERNAME: Optional[str] = None
    MONGO_PASSWORD: Optional[str] = None
    READ_SECONDARY: bool = False


mongo_config = MongoConfig()
