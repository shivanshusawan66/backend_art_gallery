from pydantic import BaseModel
from typing import List
from datetime import datetime

from ai_mf_backend.models.v1.api import Response


class CustomMutualFundOverviewCustomResponse(Response):
    pass


class AnnualReturnCustomResponse(Response):
    pass


class PerformanceDataCustomResponse(Response):
    pass


class RiskStatisticsCustomResponse(Response):
    pass


class TrailingReturnCustomResponse(Response):
    pass


class HistoricalDataCustomResponse(Response):
    pass


class CustomMutualFundOverviewResponseData(BaseModel):
    fund_id: int
    name: str
    q_param: str
    nav: float
    symbol: str


class PerformanceDataResponseData(BaseModel):
    fund_id: int
    ytd_return: float
    average_return_5y: float
    number_of_years_up: int
    number_of_years_down: int
    best_1y_total_return: float
    worst_1y_total_return: float
    best_3y_total_return: float
    worst_3y_total_return: float


class AnnualReturnObject(BaseModel):
    year: int
    fund_return: float


class AnnualReturnResponseData(BaseModel):
    fund_id: int
    annual_returns: List[AnnualReturnObject]


class RiskStatisticsObject(BaseModel):

    period: str
    alpha: float
    beta: float
    mean_annual_return: float
    r_squared: float
    standard_deviation: float
    sharpe_ratio: float
    treynor_ratio: float


class RiskStatisticsResponseData(BaseModel):
    fund_id: int
    risk_statistics: List[RiskStatisticsObject]


class TrailingReturnObject(BaseModel):
    metric: str
    fund_return: float
    benchmark_return: float


class TrailingReturnResponseData(BaseModel):
    fund_id: int
    trailing_return: List[TrailingReturnObject]


class HistoricalDataObject(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int


class HistoricalDataResponseData(BaseModel):
    fund_id: int
    historical_data: List[HistoricalDataObject]
