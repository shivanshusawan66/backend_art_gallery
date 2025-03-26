from typing import Optional, List, Dict, Any


def process_fields(fields: Optional[str], all_fields: List[str]) -> List[str]:
    """
    Process the 'fields' argument to return a list of valid fields to project.

    Args:
    - fields (Optional[str]): Comma-separated list of fields to include.
    - all_fields (List[str]): List of valid fields.
    - exclude_id (bool): Whether to exclude "id" from the valid fields (default is False).

    Returns:
    - List[str]: List of valid fields to project.
    """
    if fields:
        requested_fields = [field.strip() for field in fields.split(",")]

        invalid_fields = [
            field for field in requested_fields if field not in all_fields
        ]
        if invalid_fields:
            raise ValueError(f"Invalid field(s) requested: {', '.join(invalid_fields)}")

        fields_to_project = ["id"] + [
            field for field in requested_fields if field in all_fields
        ]
    else:

        fields_to_project = all_fields

    return fields_to_project

def validate_query_params(query_params: Dict[str, Any], allowed_params: List[str]) -> Dict[str, Any]:
    """
    Validate that the keys in the query_params dictionary are within the allowed parameters.

    Args:
        query_params (Dict[str, Any]): Dictionary of query parameters from the request.
        allowed_params (List[str]): List of allowed query parameter names.

    Returns:
        Dict[str, Any]: The original query_params dictionary if all keys are valid.

    Raises:
        ValueError: If any query parameter is not allowed.
    """
    requested_params = list(query_params.keys())
    invalid_params = [param for param in requested_params if param not in allowed_params]
    
    if invalid_params:
        raise ValueError(f"Invalid query parameter(s) requested: {invalid_params}")
    
    return query_params
