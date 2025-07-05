from skti_system_backend.config.v1 import BaseSettingsWrapper


class AuthenticationConfig(BaseSettingsWrapper):
    """
    Authentication Configuration class that sets up a BaseSettingsWrapper with a SECRET key

    :param SECRET: A secret key used for authentication
    :type SECRET: str

    :returns: An instance of the AuthenticationConfig class with a specified SECRET key
    :return type: AuthenticationConfig instance
    """

    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str 




authentication_config = AuthenticationConfig()
