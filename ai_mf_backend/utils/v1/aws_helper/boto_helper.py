from typing import Dict 

import boto3

from ai_mf_backend.config.v1.aws_config import aws_config

from ai_mf_backend.utils.v1.generic_helper import Singleton


class BotoHelper(Singleton):
    def __init__(self, api_key: Dict = None):

        aws_access_key_id = (
            api_key["aws_access_key_id"]
            if "aws_access_key_id" in api_key
            else aws_config.AWS_ACCESS_KEY_ID
        )
        aws_secret_access_key = (
            api_key["aws_secret_access_key"]
            if "aws_secret_access_key" in api_key
            else aws_config.AWS_SECRET_ACCESS_KEY
        )
        aws_session_token = (
            api_key["aws_session_token"]
            if "aws_session_token" in api_key
            else aws_config.AWS_SESSION_TOKEN
        )

        self.boto3_session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )

    def bedrock(self):
        client = self.boto3_session.client(
            service_name="bedrock-runtime", region_name=aws_config.AWS_REGION
        )

        return client
