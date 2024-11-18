from typing import Optional
from pydantic import BaseModel
from ai_mf_backend.models.v1.api import Response
from datetime import date


# Request model for updating UserFinancialDetails
class UserPersonalFinancialDetailsUpdateRequest(BaseModel):
    user_id: int
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender_id: Optional[int] = None
    marital_status_id: Optional[int] = None
    occupation_id: Optional[int] = None
    annual_income_id: Optional[int] = None
    monthly_saving_capacity_id: Optional[int] = None
    investment_amount_per_year_id: Optional[int] = None
    regular_source_of_income: Optional[bool] = None
    lock_in_period_accepted: Optional[bool] = None
    investment_style: Optional[str] = None


# Response model for updating UserFinancialDetails
class UserPersonalFinancialDetailsUpdateResponse(Response):
    pass
