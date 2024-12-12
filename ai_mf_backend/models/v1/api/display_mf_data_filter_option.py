from pydantic import BaseModel
from typing import Dict, List, Optional


class FundFamiliesResponseModel(BaseModel):
    fund_family: List[str]
    morningstar_ratings: List[int]
    min_initial_investment: List[float]


class APIResponse(BaseModel):
    status: bool
    message: str
    data: Optional[FundFamiliesResponseModel] = None
    status_code: int
