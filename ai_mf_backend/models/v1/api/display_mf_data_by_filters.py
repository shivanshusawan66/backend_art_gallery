from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date


class MutualFundModel(BaseModel):
    scheme_name: str
    net_asset_value: Decimal
    ytd_return: Optional[Decimal] = None
    morningstar_rating: Optional[str] = None
    fund_family: Optional[str] = None
    min_investment: Decimal
    performance_ytd_return: Optional[Decimal] = None
    performance_average_return_5y: Optional[Decimal] = None

    # Additional fields from FundOverview
    category: Optional[str] = None
    net_assets: Optional[Decimal] = None
    yield_value: Optional[Decimal] = None
    inception_date: Optional[date] = None

    # Additional fields from PerformanceData
    morningstar_return_rating: Optional[str] = None
    number_of_years_up: int = 0
    number_of_years_down: int = 0
    best_3y_total_return: Optional[Decimal] = Decimal(0.00)
    worst_3y_total_return: Optional[Decimal] = Decimal(0.00)

    # Additional fields from FundData
    min_subsequent_investment: Optional[Decimal] = Decimal(0.00)

    # Additional fields from RiskStatistics (if needed)
    alpha: Optional[Decimal] = Decimal(0.00)
    beta: Optional[Decimal] = Decimal(0.00)
    mean_annual_return: Optional[Decimal] = Decimal(0.00)
    r_squared: Optional[Decimal] = Decimal(0.00)
    standard_deviation: Optional[Decimal] = Decimal(0.00)
    sharpe_ratio: Optional[Decimal] = Decimal(0.00)
    treynor_ratio: Optional[Decimal] = Decimal(0.00)


class MutualFundFilterResponse(BaseModel):
    status: bool
    message: str
    data: List[MutualFundModel]
    total_count: int
    current_page: int
    total_pages: int
    status_code: int


class ErrorResponse(BaseModel):
    status: bool
    message: str
    status_code: int
