import logging
from typing import Dict, Any, List, Set, Tuple, Type, Union
from django.db.models import Model,Q
from django.db import transaction
from ai_mf_backend.utils.v1.errors import FetchDataFromApiException


logger = logging.getLogger(__name__)


def process_and_store_data(
    data: List[Dict[str, Any]],
    model_class: Type[Model],
    primary_key_fields: Union[List[str], Tuple[str, ...]],
    batch_size: int = 1000,
) -> None:
    """
    Bulk process data for insert, update, and delete operations in atomic batches.

    Args:
        data: List of dicts containing raw rows (each may have a 'flag').
        model_class: Django model class to operate on.
        batch_size: Number of rows per batch.
        primary_key_fields: Single PK field name or tuple of fields for composite PKs.
    """
    if not data:
        logger.warning("No data received to process")
        raise FetchDataFromApiException("No data received to process")

    # Normalize PK fields to tuple
    if isinstance(primary_key_fields, str):
        pk_fields: Tuple[str, ...] = (primary_key_fields,)
    else:
        pk_fields = tuple(primary_key_fields)

    # Ensure PKs exist on model
    model_fields: Set[str] = {f.name for f in model_class._meta.fields}
    missing = set(pk_fields) - model_fields
    if missing:
        raise FetchDataFromApiException(f"Primary key fields not in model: {missing}")

    # Process in batches
    for batch_num, chunk in enumerate(_chunked(data, batch_size), start=1):
        delete_keys, upsert_rows = _classify_rows(chunk, model_fields, pk_fields)
        with transaction.atomic():
            _perform_deletes(model_class, delete_keys, pk_fields, batch_num)
            perform_bulk_upsert(model_class, upsert_rows, pk_fields, model_fields, batch_num,batch_size)


def _chunked(iterable: List[Any], size: int):
    """Yield successive chunks of given size."""
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def _classify_rows(
    batch: List[Dict[str, Any]],
    model_fields: Set[str],
    pk_fields: Tuple[str, ...]
) -> Tuple[Set[Tuple[Any, ...]], List[Dict[str, Any]]]:
    """
    Separate rows for deletion vs upsert based on a 'flag' key.

    Returns:
        delete_keys: Set of PK tuples to delete.
        upsert_rows: List of cleaned dicts to insert/update.
    """
    delete_keys: Set[Tuple[Any, ...]] = set()
    upsert_rows: List[Dict[str, Any]] = []

    for raw in batch:
        flag = raw.get('flag', 'A')
        cleaned: Dict[str, Any] = {}

        for key, val in raw.items():
            norm = f"_{key}" if key and key[0].isdigit() else key
            if norm in model_fields:
                cleaned[norm] = val


        if not all(pk in cleaned for pk in pk_fields):
            continue
        pk_tuple = tuple(cleaned[pk] for pk in pk_fields)
        if flag == 'D':
            delete_keys.add(pk_tuple)
        else:
            upsert_rows.append(cleaned)

    return delete_keys, upsert_rows


def _perform_deletes(
    model_class: Type[Model],
    delete_keys: Set[Tuple[Any, ...]],
    pk_fields: Tuple[str, ...],
    batch_num: int
) -> None:
    """
    Delete records matching each PK tuple.
    """
    for pk in delete_keys:
        filters = dict(zip(pk_fields, pk))
        deleted_count, _ = model_class.objects.filter(**filters).delete()
        logger.info(f"Batch {batch_num}: Deleted {deleted_count} rows for PK {pk}")


def perform_bulk_upsert(
    model_class: Type[Model],
    rows: List[Dict[str, Any]],
    pk_fields: Tuple[str, ...],
    model_fields: Set[str],
    batch_num: int = 1,
    chunk_size: int = 1000,
) -> Dict[str, int]:
    if not rows:
        logger.debug("No rows provided for upsert operation")

    rows_by_pk = {
        tuple(row[pk] for pk in pk_fields): row
        for row in rows
    }
    

    queries = []
    for pk_values in rows_by_pk.keys():
        q_obj = Q()
        for field, value in zip(pk_fields, pk_values):
            q_obj &= Q(**{field: value})
        queries.append(q_obj)
    
    if not queries:
        return {"created": 0, "updated": 0}
    
    combined_query = queries[0]
    for q in queries[1:]:
        combined_query |= q
    
    existing_objects = list(model_class.objects.filter(combined_query))
    
    existing_map = {
        tuple(getattr(obj, field) for field in pk_fields): obj
        for obj in existing_objects
    }
    
    to_update = []
    to_create = []
    
    for pk_tuple, row_data in rows_by_pk.items():
        if pk_tuple in existing_map:
            obj = existing_map[pk_tuple]
            for field, value in row_data.items():
                if field in model_fields:
                    setattr(obj, field, value)
            to_update.append(obj)
        else:
            filtered_data = {k: v for k, v in row_data.items() if k in model_fields}
            to_create.append(model_class(**filtered_data))
    
    update_fields = list(model_fields - set(pk_fields))
    update_fields = [f for f in update_fields if f != "id"]
    
    created_count = 0
    updated_count = 0
    
    with transaction.atomic():
        for i in range(0, len(to_update), chunk_size):
            chunk = to_update[i:i + chunk_size]
            if chunk:
                model_class.objects.bulk_update(chunk, update_fields)
                updated_count += len(chunk)
                logger.info(f"Batch {batch_num}: Updated chunk {i//chunk_size + 1} with {len(chunk)} records")

        for i in range(0, len(to_create), chunk_size):
            chunk = to_create[i:i + chunk_size]
            if chunk:
                model_class.objects.bulk_create(chunk,ignore_conflicts=True)
                created_count += len(chunk)
                logger.info(f"Batch {batch_num}: Created chunk {i//chunk_size + 1} with {len(chunk)} records")
    
    logger.info(f"Batch {batch_num}: Completed - Created {created_count} and updated {updated_count} records")
