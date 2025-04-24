from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date
from ai_mf_backend.models.v1.api import Response



class FundOverview(BaseModel):
    net_assets_value: Optional[float]
    three_year_return: Optional[float]
    five_year_return: Optional[float]
    



class FundRiskStatistics(BaseModel):
    one_year_return: Optional[float]
    sharpe_ratio: Optional[float]
    std_dev: Optional[float]
    beta: Optional[float]
    jalpha: Optional[float]
    treynor: Optional[float]


class ReturnsCalculator(BaseModel):
    sip: Optional[str] = None


class AssetAllocation(BaseModel):
    large_cap_percent: Optional[float]
    mid_cap_percent: Optional[float]
    small_cap_percent: Optional[float]
    others_cap_percentage: Optional[float]


class TopHolding(BaseModel):
    holding_name: Optional[str]
    weight: float


class TopSector(BaseModel):
    sector_name: Optional[str]
    weight:  Optional[float]

class FundManagerDetails(BaseModel):
    initial: Optional[str]
    fundmanager: Optional[str]
    qualification: Optional[str]
    basicdetails: Optional[str]
    experience: Optional[str]
    designation: Optional[str]
    age: Optional[int]

class FundDescriptionDetails(BaseModel):
    short_description: Optional[str]
    long_description: Optional[str]

class AbsoluteAndAnnualisedReturn(BaseModel):
    absolute_1yr_return : Optional[float]
    absolute_3yr_return : Optional[float]
    absolute_5yr_return : Optional[float]
    annualised_1_yr_return : Optional[float]
    annualised_3_yr_return : Optional[float]
    annualised_5yr_return : Optional[float]


class NavHistory(BaseModel):
    data: Optional[List[Dict[str, Any]]]
    

# here not use response because we do not require key data that'why we donot inherit form response
class MutualFundDashboardResponse(BaseModel):
    status: bool
    message: str
    status_code: Optional[int] = 200
    fund_history_nav: Optional[NavHistory] = None
    fund_overview: Optional[FundOverview] = None
    fund_risk_statistics: Optional[FundRiskStatistics] = None
    returns_calculator: Optional[ReturnsCalculator] = None
    asset_allocation: Optional[AssetAllocation] = None
    top_holdings: Optional[List[TopHolding]] = None
    top_sectors: Optional[List[TopSector]] = None
    fund_manager_details: Optional[List[FundManagerDetails]] = None
    fund_description: Optional[FundDescriptionDetails] = None
    absolute_and_annualised_return: Optional[AbsoluteAndAnnualisedReturn] = None



class MutualFundFilterResponse(Response):
    data: List[Dict[str, Any]]
    page: int
    total_pages: int
    total_data: int
    
