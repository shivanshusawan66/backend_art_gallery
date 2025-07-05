from typing import Optional
from skti_system_backend.config.v1 import BaseSettingsWrapper

class PostgresConfig(BaseSettingsWrapper):
    """
    Configuration settings for PostgreSQL database connection.

    :param POSTGRES_DB_NAME: Name of the PostgreSQL database.
    :type POSTGRES_DB_NAME: str

    :param POSTGRES_HOST: Hostname of the PostgreSQL database.
    :type POSTGRES_HOST: str

    :param POSTGRES_USERNAME: Username for PostgreSQL authentication, Optional.
    :type POSTGRES_USERNAME: Optional[str]

    :param POSTGRES_PASSWORD: Password for PostgreSQL authentication, Optional.
    :type POSTGRES_PASSWORD: Optional[str]

    :param POSTGRES_PORT: Port for PostgreSQL connection, Optional. Default is 5432.
    :type POSTGRES_PORT: Optional[int]
    """

    POSTGRES_DB_NAME: str = "artwork_db_9y4i"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_USERNAME: Optional[str]
    POSTGRES_PASSWORD: Optional[str]
    POSTGRES_PORT: Optional[int] = 5432


postgres_config = PostgresConfig()
