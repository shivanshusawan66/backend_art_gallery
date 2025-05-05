# models.py
from typing import Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

from ai_mf_backend.models.v1.api import Response


class InsertPortfolio(BaseModel):
    scheme_code: int
    fund_name: Optional[str] = None
    investment_date: datetime
    invested_amount: float
    quantity: float
    current_fund_nav: Optional[float] = None
    investment_type: str
    frequency: Optional[str] = None


class GetPortfolio(BaseModel):
    investment_id: Optional[int] = None
    scheme_code: int
    fund_name: Optional[str] = None
    fund_type: Optional[str] = None
    fund_category: Optional[str] = None
    investment_date: datetime
    invested_amount: float
    quantity: float
    current_fund_nav: Optional[float] = None
    investment_type: str
    frequency: Optional[str] = None

class UpdatePortfolio(BaseModel):
    investment_id: Optional[int] = None
    scheme_code: int
    fund_name: Optional[str] = None
    investment_date: datetime
    invested_amount: float
    quantity: float
    current_fund_nav: Optional[float] = None
    investment_type: str
    frequency: Optional[str] = None

class UpdatePortfolio(BaseModel):
    investment_id: Optional[int] = None
    scheme_code: int
    fund_name: Optional[str] = None
    investment_date: datetime
    invested_amount: float
    quantity: float
    current_fund_nav: Optional[float] = None
    investment_type: str
    frequency: str


class GetPortfolioResponse(Response):
    pass


class DeletePortfolioRequest(BaseModel):
    investment_id: int
    is_real: bool


class MFOptionandDetailsResponse(Response):
    data: list[dict[str, Any]]


class DeletePortfolioResponse(Response):
    pass


class AddPortfolioRequest(BaseModel):
    user_id: int
    is_real: int

    investments: List[InsertPortfolio]


class AddPortfolioResponse(Response):
    pass


class PatchPortfolioRequest(BaseModel):
    user_id: int
    is_real: int

    investments: List[UpdatePortfolio]


class PatchPortfolioResponse(Response):
    pass