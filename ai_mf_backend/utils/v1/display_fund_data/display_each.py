from typing import List, Optional, Union

from datetime import datetime


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
