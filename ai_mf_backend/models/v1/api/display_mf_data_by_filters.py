from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from decimal import Decimal
from datetime import date


class TrailingReturnModel(BaseModel):
    metric: Optional[str] = None
    fund_return: Optional[Decimal] = None


class AnnualReturnModel(BaseModel):
    year: Optional[int] = None
    fund_return: Optional[Decimal] = None


class MutualFundModel(BaseModel):
    fund_id: Optional[int] = None
    scheme_name: Optional[str] = None
    net_asset_value: Optional[Decimal] = None
    morningstar_rating: Optional[str] = None
    fund_family: Optional[str] = None
    min_investment: Optional[Decimal] = None

    # Optional fields that will be excluded if None
    ytd_return: Optional[Decimal] = None
    net_assets: Optional[Decimal] = None
    yield_value: Optional[Decimal] = None
    inception_date: Optional[date] = None
    performance_ytd_return: Optional[Decimal] = None
    performance_average_return_5y: Optional[Decimal] = None
    number_of_years_up: Optional[int] = None
    number_of_years_down: Optional[int] = None
    best_3y_total_return: Optional[Decimal] = None
    worst_3y_total_return: Optional[Decimal] = None
    alpha: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    mean_annual_return: Optional[Decimal] = None
    r_squared: Optional[Decimal] = None
    standard_deviation: Optional[Decimal] = None
    sharpe_ratio: Optional[Decimal] = None
    treynor_ratio: Optional[Decimal] = None

    trailing_returns: Optional[List[TrailingReturnModel]] = None
    annual_returns: Optional[List[AnnualReturnModel]] = None

    model_config = ConfigDict(
        json_encoders={Decimal: str},
    )


class MutualFundFilterResponse(BaseModel):
    status: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[List[MutualFundModel]] = None
    total_count: Optional[int] = None
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    status_code: Optional[int] = None
