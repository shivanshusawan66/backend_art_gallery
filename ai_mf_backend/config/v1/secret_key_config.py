from typing import Optional
from config.v1 import BaseSettingsWrapper


class Secret_key_config(BaseSettingsWrapper):

    SECRET_KEY: str


secret_config = Secret_key_config()
