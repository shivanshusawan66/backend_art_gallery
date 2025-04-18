import logging
from typing import Dict, Any, List, Type
from django.db.models import Model
from django.db import transaction
from ai_mf_backend.utils.v1.errors import FetchDataFromApiException


logger = logging.getLogger(__name__)


def process_and_store_data(
    data: List[Dict[str, Any]], model_class: Type[Model], batch_size: int = 1000
) -> Dict[str, Any]:
    print("entered processing dta")

    try:
        if not data:
            logger.warning("No data received to process")
            raise FetchDataFromApiException("No data received to process")

        model_fields = {f.name for f in model_class._meta.fields}
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            instances = []

            for item in batch:
                filtered_item = {
                    ("_" + k if k and k[0].isdigit() else k): v
                    for k, v in item.items()
                    if ("_" + k if k and k[0].isdigit() else k) in model_fields
                }
                instance = model_class(**filtered_item)
                instances.append(instance)

            with transaction.atomic():
                model_class.objects.bulk_create(instances)
                logger.info(
                    f"Created {len(instances)} instances in batch {i // batch_size + 1}"
                )

    except Exception as e:
        logger.exception(f"Error in process_and_store_data: {str(e)}")
        raise FetchDataFromApiException(f"Error in process_and_store_data: {str(e)}")
