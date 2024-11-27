from pydantic import BaseModel
from typing import List, Optional


class FundFamiliesResponseModel(BaseModel):
    fund_family: List[str]
    morningstar_ratings: List[int]
    min_initial_investment: List[float]


class SuccessResponse(BaseModel):
    status: bool
    message: str
    data: Optional[FundFamiliesResponseModel] = None
    status_code: int


class ErrorResponse(BaseModel):
    status: bool
    message: str
    error_details: Optional[str] = None
    status_code: int

    class Config:
        orm_mode = True
