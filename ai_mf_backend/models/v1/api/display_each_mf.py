from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi import Query

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





class AnnualReturnObject(BaseModel):
    year: int
    fund_return: float = None


class AnnualReturnResponseData(BaseModel):
    fund_id: int
    annual_returns: List[AnnualReturnObject]


class RiskStatisticsObject(BaseModel):

    period: str = None
    alpha: float = None
    beta: float = None
    mean_annual_return: float = None
    r_squared: float = None
    standard_deviation: float = None
    sharpe_ratio: float = None
    treynor_ratio: float = None


class RiskStatisticsResponseData(BaseModel):
    fund_id: int
    risk_statistics: List[RiskStatisticsObject]


class TrailingReturnObject(BaseModel):
    metric: str = None
    fund_return: float = None
    benchmark_return: float = None


class TrailingReturnResponseData(BaseModel):
    fund_id: int
    trailing_return: List[TrailingReturnObject]


class HistoricalDataObject(BaseModel):
    date: datetime = None
    open: float = None
    high: float = None
    low: float = None
    close: float = None
    adj_close: float = None
    volume: int = None


class HistoricalDataResponseData(BaseModel):
    fund_id: int
    historical_data: List[HistoricalDataObject]
