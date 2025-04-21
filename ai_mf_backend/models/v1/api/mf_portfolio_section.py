# models.py
from typing import Any, Optional
from pydantic import BaseModel
from datetime import date

from ai_mf_backend.models.v1.api import Response


class Portfolio(BaseModel):
    user_id: int
    scheme_code : int
    mutual_fund: str
    investment_date: date
    invested_amount: float
    quantity: float
    current_value: float
    returns: float
    investment_type : str 
    frequency : Optional[str] 
    nav : float 
    fund_type : str
    fund_cap : str

class PortfolioResponse(Response):
    data: list[dict[str, Any]]

class MFOptionandDetailsResponse(Response):
    data: list[dict[str, Any]]
