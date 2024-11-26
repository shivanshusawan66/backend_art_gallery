from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class MutualFundModel(BaseModel):
    scheme_name: str
    net_asset_value: Decimal
    ytd_return: Optional[Decimal] = None
    morningstar_rating: Optional[str] = None
    fund_family: Optional[str] = None
    min_investment: Decimal


class MutualFundFilterResponse(BaseModel):
    status: bool
    message: str
    data: List[MutualFundModel]
    status_code: int
    total_count: Optional[int] = None
    current_page: Optional[int] = None
    total_pages: Optional[int] = None


class ErrorResponse(BaseModel):
    status: bool
    message: str
    detail: Optional[str] = None
    status_code: int
