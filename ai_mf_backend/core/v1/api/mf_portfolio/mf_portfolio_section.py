# dummy_api.py

from fastapi import APIRouter
from typing import List
from ai_mf_backend.models.v1.api.mf_portfolio_section import Portfolio,PortfolioResponse
from datetime import date

router = APIRouter()

def format_returns(p) -> str:
    diff = p.current_value - p.invested_amount
    percent = (diff / p.invested_amount * 100) if p.invested_amount else 0
    return f"{round(percent)}% | ₹{int(diff):,}"

@router.get("/mf_portfolio_section_real/{user_id}", response_model=PortfolioResponse)
def get_portfolio(user_id : int):
    dummy_data =[
        Portfolio(
            user_id=23,
            scheme_code = 120,
            mutual_fund="HDFC Nifty 50 Index Direct Growth Plan",
            investment_date=date(2023, 1, 1),
            invested_amount=10000,
            quantity=300,
            current_value=12000,
            returns=2000,
            investment_type="SIP",
            frequency="Monthly",
            nav=40.0,
            fund_type="equity",
            fund_cap="Large Cap"
        ),
        Portfolio(
            user_id=28,
            scheme_code = 400,
            mutual_fund="UTI Nifty Midcap Direct Growth Plan",
            investment_date=date(2021, 11, 21),
            invested_amount=110000,
            quantity=500,
            current_value=90000,
            returns=-20000,
            investment_type="Lumpsum",
            frequency="NA",
            nav=180.0,
            fund_type="debt",
            fund_cap="Mid Cap"
        ),
        Portfolio(
            user_id=28,
            scheme_code = 410,
            mutual_fund="UTI Nifty Midcap Direct Growth Plan New",
            investment_date=date(2021, 11, 21),
            invested_amount=110000,
            quantity=500,
            current_value=90000,
            returns=-20000,
            investment_type="Lumpsum",
            frequency="NA",
            nav=180.0,
            fund_type="equity",
            fund_cap="Mid Cap"
        ),
        Portfolio(
            user_id=42,
            scheme_code = 412,
            mutual_fund="ICICI Value Discovery Fund",
            investment_date=date(2022, 6, 15),
            invested_amount=50000,
            quantity=200,
            current_value=65000,
            returns=15000,
            investment_type="SIP",
            frequency="Monthly",
            nav=325.0,
            fund_type="equity",
            fund_cap="Small Cap"
        )
    ]
    user_data = [
        {
            "mutual_fund": p.mutual_fund,
            "investment_date": p.investment_date,
            "returns": format_returns(p),
            "invested_amount": p.invested_amount,
            "quantity": p.quantity,
            "current_value": p.current_value,
            "fund_type": p.fund_type,
            "fund_cap": p.fund_cap
        }
        for p in dummy_data if p.user_id == user_id
    ]
    if not user_data:
        return PortfolioResponse(
            status = False,
            message="User is not Registered Yet",
            data = user_data,
            status_code=400
        )
    
    return PortfolioResponse(
        status=True,
        message="Portfolio fetched successfully",
        data=user_data
    )

@router.get("/mf_portfolio_section_trial/{user_id}", response_model=PortfolioResponse)
def get_portfolio(user_id : int):
    dummy_data =[
        Portfolio(
            user_id=23,
            scheme_code = 120,
            mutual_fund="HDFC Nifty 50 Index Direct Growth Plan",
            investment_date=date(2023, 1, 1),
            invested_amount=10000,
            quantity=300,
            current_value=12000,
            returns=2000,
            investment_type="SIP",
            frequency="Monthly",
            nav=40.0,
            fund_type="equity",
            fund_cap="Large Cap"
        ),
        Portfolio(
            user_id=28,
            scheme_code = 400,
            mutual_fund="UTI Nifty Midcap Direct Growth Plan",
            investment_date=date(2021, 11, 21),
            invested_amount=110000,
            quantity=500,
            current_value=90000,
            returns=-20000,
            investment_type="Lumpsum",
            frequency="NA",
            nav=180.0,
            fund_type="debt",
            fund_cap="Mid Cap"
        ),
        Portfolio(
            user_id=28,
            scheme_code = 410,
            mutual_fund="UTI Nifty Midcap Direct Growth Plan New",
            investment_date=date(2021, 11, 21),
            invested_amount=110000,
            quantity=500,
            current_value=90000,
            returns=-20000,
            investment_type="Lumpsum",
            frequency="NA",
            nav=180.0,
            fund_type="equity",
            fund_cap="Mid Cap"
        ),
        Portfolio(
            user_id=42,
            scheme_code = 412,
            mutual_fund="ICICI Value Discovery Fund",
            investment_date=date(2022, 6, 15),
            invested_amount=50000,
            quantity=200,
            current_value=65000,
            returns=15000,
            investment_type="SIP",
            frequency="Monthly",
            nav=325.0,
            fund_type="equity",
            fund_cap="Small Cap"
        )
    ]
    user_data = [
        {
            "mutual_fund": p.mutual_fund,
            "investment_date": p.investment_date,
            "returns": format_returns(p),
            "invested_amount": p.invested_amount,
            "quantity": p.quantity,
            "current_value": p.current_value,
            "fund_type": p.fund_type,
            "fund_cap": p.fund_cap
        }
        for p in dummy_data if p.user_id == user_id
    ]
    if not user_data:
        return PortfolioResponse(
            status = False,
            message="User is not Registered Yet",
            data = user_data,
            status_code=400
        )
    
    return PortfolioResponse(
        status=True,
        message="Portfolio fetched successfully",
        data=user_data
    )

