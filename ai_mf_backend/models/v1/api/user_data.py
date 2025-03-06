from typing import List, Optional
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


class UserPersonalFinancialFormData(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[str] = None
    monthly_saving_capacity: Optional[str] = None
    investment_amount_per_year: Optional[str] = None
    regular_source_of_income: Optional[bool] = None
    lock_in_period_accepted: Optional[bool] = None
    investment_style: Optional[str] = None


class UserPersonalFinancialDetailsResponsesDisplayResponse(Response):
    pass


class OptionModel(BaseModel):
    option_id: int
    label: str

class QuestionDataModel(BaseModel):
    question_id: int
    question_label: str
    options: List[OptionModel]
    required: bool
    type: str

class UserProfileQuestionResponse(Response):
    section_id: Optional[int] = None
    data: Optional[List[QuestionDataModel]] = None