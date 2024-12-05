from typing import TypeVar, List, Generic, Tuple
from math import ceil

T = TypeVar("T")


class PaginationResult(Generic[T]):
    """
    Generic pagination result class that encapsulates paginated data
    and pagination metadata.
    """

    def __init__(self, items: List[T], total_count: int, page: int, page_size: int):
        self.items = items
        self.total_count = total_count
        self.page = page
        self.page_size = page_size
        self.total_pages = ceil(total_count / page_size)


def paginate_queryset(queryset, page: int = 1, page_size: int = 10) -> Tuple[List, int]:
    """
    Utility function to paginate a queryset.

    Args:
        queryset: The queryset to paginate
        page: Current page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (paginated_items, total_count)
    """
    # Ensure page and page_size are positive
    page = max(1, page)
    page_size = max(1, min(page_size, 100))  # Limit max page size to 100

    # Calculate total count
    total_count = queryset.count()

    # Calculate start and end indices
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    # Slice the queryset
    paginated_items = list(queryset[start_idx:end_idx])

    return paginated_items, total_count
