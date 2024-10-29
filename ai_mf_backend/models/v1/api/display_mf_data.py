from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal


# Pydantic models
class MutualFundModel(BaseModel):
    id: int
    scheme_name: str
    q_param: str
    net_asset_value: Decimal
    date: date
    symbol: str

    class Config:
        orm_mode = True  # Enable ORM mode
        from_attributes = True  # Allow from_orm to work with attributes


class FundOverviewModel(BaseModel):
    id: int
    fund_id: int
    category: Optional[str]
    fund_family: Optional[str]
    net_assets: Optional[Decimal]
    ytd_return: Optional[Decimal]
    yield_value: Optional[Decimal]
    morningstar_rating: Optional[str]
    inception_date: Optional[date]

    class Config:
        orm_mode = True  # Enable ORM mode
        from_attributes = True  # Allow from_orm to work with attributes


class HistoricalDataModel(BaseModel):
    id: int
    fund_id: int
    date: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adj_close: Decimal
    volume: int

    class Config:
        orm_mode = True  # Enable ORM mode
        from_attributes = True  # Allow from_orm to work with attributes


class PerformanceDataModel(BaseModel):
    id: int
    fund_id: int
    morningstar_return_rating: Optional[str]
    ytd_return: Decimal
    average_return_5y: Decimal
    number_of_years_up: int
    number_of_years_down: int
    best_1y_total_return: Decimal
    worst_1y_total_return: Decimal
    best_3y_total_return: Decimal
    worst_3y_total_return: Decimal

    class Config:
        orm_mode = True  # Enable ORM mode
        from_attributes = True  # Allow from_orm to work with attributes


class TrailingReturnModel(BaseModel):
    id: int
    fund_id: int
    metric: str
    fund_return: Decimal
    benchmark_return: Decimal

    class Config:
        orm_mode = True  # Enable ORM mode
        from_attributes = True  # Allow from_orm to work with attributes


class AnnualReturnModel(BaseModel):
    id: int
    fund_id: int
    year: int
    fund_return: Decimal
    category_return: Decimal

    class Config:
        orm_mode = True  # Enable ORM mode
        from_attributes = True  # Allow from_orm to work with attributes


class FundDataModel(BaseModel):
    id: int
    fund_id: int
    min_initial_investment: Decimal
    min_subsequent_investment: Decimal

    class Config:
        orm_mode = True  # Enable ORM mode
        from_attributes = True  # Allow from_orm to work with attributes


class RiskStatisticsModel(BaseModel):
    id: int
    fund_id: int
    period: str
    alpha: Decimal
    beta: Decimal
    mean_annual_return: Decimal
    r_squared: Decimal
    standard_deviation: Decimal
    sharpe_ratio: Decimal
    treynor_ratio: Decimal

    class Config:
        orm_mode = True  # Enable ORM mode
        from_attributes = True  # Allow from_orm to work with attributes


class ComprehensiveFundDataModel(BaseModel):
    mutual_fund: Optional[MutualFundModel] = None
    fund_overview: Optional[FundOverviewModel] = None
    performance_data: Optional[List[PerformanceDataModel]] = (
        None  # List for multiple entries
    )
    trailing_returns: Optional[List[TrailingReturnModel]] = (
        None  # List for multiple entries
    )
    annual_returns: Optional[List[AnnualReturnModel]] = (
        None  # List for multiple entries
    )
    fund_data: Optional[FundDataModel] = None
    risk_statistics: Optional[List[RiskStatisticsModel]] = (
        None  # List for multiple entries
    )

    class Config:
        orm_mode = True  # Enable ORM mode
        from_attributes = True  # Allow from_orm to work with attributes


# Pydantic model for paginated request
class PaginatedRequestModel(BaseModel):
    page: Optional[int] = Field(
        1, ge=1, description="Page number must be greater than 0"
    )
    page_size: Optional[int] = Field(
        10, ge=1, description="Page size must be greater than 0"
    )

    @validator("page", "page_size")
    def validate_pagination(cls, value):
        if value < 1:
            raise ValueError("Page and page size must be greater than 0")
        return value


# Pydantic model for FundRequest
class FundRequestModel(BaseModel):
    fund_id: str = Field(
        ..., min_length=1, description="Fund ID must be a non-empty string"
    )

    @validator("fund_id")
    def validate_fund_id(cls, value):
        if not value or value.strip() == "":
            raise ValueError("Fund ID cannot be None or an empty string")
        return value


class HistoricalDataRequestModel(BaseModel):
    fund_id: str = Field(
        ..., min_length=1, description="Fund ID must be a non-empty string"
    )
    page: Optional[int] = Field(
        1, ge=1, description="Page number must be greater than 0"
    )
    page_size: Optional[int] = Field(
        10, ge=1, description="Page size must be greater than 0"
    )

    @validator("fund_id")
    def validate_fund_id(cls, value):
        if not value or value.strip() == "":
            raise ValueError("Fund ID cannot be None or an empty string")
        return value


class FundFilterRequest(BaseModel):
    min_investment_range_start: Optional[Decimal] = Field(
        None, description="Minimum investment range start amount"
    )
    min_investment_range_end: Optional[Decimal] = Field(
        None, description="Minimum investment range end amount"
    )
    fund_family: Optional[str] = Field(None, description="Fund family name")
    morningstar_rating: Optional[str] = Field(
        None, description="Morningstar rating (1-5 stars)"
    )
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page")


# Response model for filtered funds
class FilteredFundsResponse(BaseModel):
    total_count: int
    funds: List[ComprehensiveFundDataModel]
    current_page: int
    total_pages: int
# Define the error response model
class ErrorResponseModel(BaseModel):
    status_code: int
    message: str
# Pydantic model for paginated request
class PaginatedRequestModel(BaseModel):
    page: Optional[int] = Field(
        1, ge=1, description="Page number must be greater than 0"
    )
    page_size: Optional[int] = Field(
        10, ge=1, description="Page size must be greater than 0"
    )
