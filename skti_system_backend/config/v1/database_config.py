from typing import Optional
from skti_system_backend.config.v1 import BaseSettingsWrapper


class MySQLConfig(BaseSettingsWrapper):
    """
    Configuration settings for MySQL database connection.

    :param MYSQL_DB_NAME: Name of the MySQL database.
    :type MYSQL_DB_NAME: str

    :param MYSQL_HOST: Hostname of the MySQL database.
    :type MYSQL_HOST: str

    :param MYSQL_USERNAME: Username for MySQL authentication, Optional.
    :type MYSQL_USERNAME: Optional[str]

    :param MYSQL_PASSWORD: Password for MySQL authentication, Optional.
    :type MYSQL_PASSWORD: Optional[str]

    :param MYSQL_PORT: Port for MySQL connection, Optional. Default is 3306.
    :type MYSQL_PORT: Optional[int]
    """

    MYSQL_DB_NAME: str = "artwork_db"
    MYSQL_HOST: str = "localhost"  
    MYSQL_USERNAME: Optional[str] 
    MYSQL_PASSWORD: Optional[str]  
    MYSQL_PORT: Optional[int] = 3306


mysql_config = MySQLConfig()