from typing import List, Optional, Union

from datetime import datetime


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


def process_years(years: Optional[str] = None) -> Union[List[int], None]:
    """
    Process the 'years' argument to return a list of valid years.

    Args:
    - years (Optional[str]): Comma-separated list of years to include.

    Returns:
    - List[int]: List of valid years to project.
    - None: In case no dates were provided, we will return all data

    Raises:
    - ValueError: If any requested year is invalid.
    """
    if not years:
        return None

    try:
        requested_years = [int(year.strip()) for year in years.split(",")]
    except Exception as e:
        raise ValueError(f"Invalid year range provided {e}")

    current_year = datetime.utcnow().year
    for year in requested_years:
        if year <= current_year:
            continue
        raise ValueError(
            f"Invalid year(s) requested: year should always be smaller than the current year."
        )

    return requested_years
