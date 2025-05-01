import logging
import requests
from typing import Dict, Any,Type,Union,List,Tuple
from django.db.models import Model
from celery.exceptions import MaxRetriesExceededError
from requests.exceptions import RequestException
from ai_mf_backend.core import celery_app
from ai_mf_backend.utils.v1.errors import FetchDataFromApiException
from ai_mf_backend.utils.v1.database.incremental_insert import process_and_store_data
from ai_mf_backend.utils.v1.enums import FetchApiConfig
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def fetch_and_store_api_data(
    self,
    api_url: str,
    params: Dict[str, Any],
    model_name: Type[Model],
    primary_key_fields: Union[List[str], Tuple[str, ...]], 
    batch_size: int = 1000,
) -> Dict[str, Any]:
    print("entered fetch and store api data")
    try:
        logger.info(f"Fetching data from {api_url} with params: {params}")
        response = requests.get(api_url, params=params, timeout=60)
        response.raise_for_status()
        
        if response.status_code == 204 or not response.content:
            logger.info("No data returned (204 or empty); skipping.")
            return

        payload = response.json()
        data = payload.get("Table", [])


        if not isinstance(data, list):
            raise ValueError(f"Expected 'Table' to be a list, got {type(data)}")

        return process_and_store_data(
            data=data, model_class=model_name,primary_key_fields=primary_key_fields, batch_size=batch_size
        )

    except RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        try:
            self.retry(countdown=3)
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for {api_url}")
            raise FetchDataFromApiException(f"Max retries exceeded for {api_url}")
    except Exception as e:
        logger.exception(f"Error in fetch_and_store_api_data task: {str(e)}")
        raise FetchDataFromApiException(
            f"Error in fetch_and_store_api_data task: {str(e)}"
        )


@celery_app.task
def run_all_apis():
    for config in FetchApiConfig:
        api_url, params, model_cls, batch_size, primary_keys = config.value
        fetch_and_store_api_data.delay(
            api_url=api_url,
            params=params,
            model_name=model_cls,
            batch_size=batch_size,
            primary_key_fields=primary_keys,
        )