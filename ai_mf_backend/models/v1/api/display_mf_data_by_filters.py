from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional, List, Union, Dict, Any
from datetime import date


class TrailingReturnModel(BaseModel):
    metric: Optional[str] = None
    fund_return: Optional[Decimal] = None
    benchmark_return: Optional[Decimal] = None


class AnnualReturnModel(BaseModel):
    year: Optional[int] = None
    fund_return: Optional[Decimal] = None
    category_return: Optional[Decimal] = None


class MutualFundModel(BaseModel):
    # Core fields (always included)
    fund_id: int
    scheme_name: str
    net_asset_value: Optional[Decimal] = None

    # Overview fields
    morningstar_rating: Optional[str] = None
    fund_family: Optional[str] = None

    # Optional fields with dynamic selection
    ytd_return: Optional[Decimal] = None
    net_assets: Optional[Decimal] = None
    yield_value: Optional[Decimal] = None
    inception_date: Optional[date] = None
    min_investment: Optional[Decimal] = Decimal("0")

    # Performance fields
    performance_ytd_return: Optional[Decimal] = None
    performance_average_return_5y: Optional[Decimal] = None
    number_of_years_up: Optional[int] = 0
    number_of_years_down: Optional[int] = 0
    best_3y_total_return: Optional[Decimal] = Decimal("0.00")
    worst_3y_total_return: Optional[Decimal] = Decimal("0.00")

    # Risk statistic fields
    alpha: Optional[Decimal] = Decimal("0.00")
    beta: Optional[Decimal] = Decimal("0.00")
    mean_annual_return: Optional[Decimal] = Decimal("0.00")
    r_squared: Optional[Decimal] = Decimal("0.00")
    standard_deviation: Optional[Decimal] = Decimal("0.00")
    sharpe_ratio: Optional[Decimal] = Decimal("0.00")
    treynor_ratio: Optional[Decimal] = Decimal("0.00")

    # Nested return models
    trailing_returns: Optional[List[TrailingReturnModel]] = None
    annual_returns: Optional[List[AnnualReturnModel]] = None

    # Allow additional fields for flexibility
    model_config = ConfigDict(extra="allow")


class MutualFundFilterResponse(BaseModel):
    status: bool
    message: str
    data: List[Union[Dict[str, Any], MutualFundModel]]
    total_count: int
    current_page: int
    total_pages: int
    status_code: int
