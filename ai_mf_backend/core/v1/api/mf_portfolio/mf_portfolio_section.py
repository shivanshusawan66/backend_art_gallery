from datetime import date
from django.apps import apps
from ai_mf_backend.config.v1.api_config import api_config 
from ai_mf_backend.models.v1.database.mf_master_data import MFSchemeMasterInDetails
from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable
from fastapi import APIRouter, Depends, Header, Query, Request, Response
from typing import Optional
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.api.mf_portfolio_section import(
    MFOptionandDetailsResponse,
    PortfolioResponse
)
from django.db.models import OuterRef, Subquery, F
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.utils.v1.authentication.secrets import jwt_token_checker, login_checker 
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.database.mf_portfolio import RealPortfolio
from ai_mf_backend.models.v1.api.mf_portfolio_section import Portfolio,PortfolioResponse

router = APIRouter()

def percentage_returns(p) :
    diff = p.current_value - p.invested_amount
    percent = (diff / p.invested_amount * 100) if p.invested_amount else 0
    return percent

@router.get("/mf_portfolio_section_real/{user_id}", response_model=PortfolioResponse)
def get_portfolio(user_id : int):
    dummy_data =[
        Portfolio(
            user_id=user_id,
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
            user_id=user_id,
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
        )
    ]
    user_data = [
        {
            "user_id":p.user_id,
            "mutual_fund": p.mutual_fund,
            "investment_date": p.investment_date,
            "returns_percentage": round(percentage_returns(p),2),
            "returns_value" : (p.current_value - p.invested_amount),
            "invested_amount": p.invested_amount,
            "quantity": p.quantity,
            "current_value": p.current_value,
            "fund_type": p.fund_type,
            "fund_cap": p.fund_cap
        }
        for p in dummy_data 
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
            user_id=user_id,
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
            user_id=user_id,
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
        )
    ]
    user_data = [
        {
            "user_id":p.user_id,
            "mutual_fund": p.mutual_fund,
            "investment_date": p.investment_date,
            "returns_percentage": round(percentage_returns(p),2),
            "returns_value" : (p.current_value - p.invested_amount),
            "invested_amount": p.invested_amount,
            "quantity": p.quantity,
            "current_value": p.current_value,
            "fund_type": p.fund_type,
            "fund_cap": p.fund_cap
        }
        for p in dummy_data 
    ]
    
    return PortfolioResponse(
        status=True,
        message="Portfolio fetched successfully",
        data=user_data
    )


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/get_mf_options_and_details", 
    response_model=MFOptionandDetailsResponse,
)
async def get_mf_options_and_details(
    request: Request,
    response: Response,
    fund_name: Optional[str] = Query(default=None, description="Search mutual fund name"),
):
    try:
        marker_list = ["status", "s_name", "navrs","frequency", "sip"]

        refs = await sync_to_async(lambda: list(MFReferenceTable.objects.filter(marker_name__in=marker_list)))()

        marker_to_models = {
            ref.marker_name: apps.get_model(api_config.PROJECT_NAME,ref.table_name)
            for ref in refs
            if ref.marker_name in marker_list
        }

        active_schemecodes = await sync_to_async(
            lambda: set(marker_to_models['status'].objects.filter(
                status="Active"
            ).values_list("schemecode", flat=True))
        )()

        base_query = MFSchemeMasterInDetails.objects.filter(schemecode__in=active_schemecodes)
        
        if fund_name:
            base_query = base_query.filter(s_name__icontains=fund_name)

        if "navrs" in marker_to_models:
            base_query = base_query.annotate(navrs=Subquery(
                marker_to_models["navrs"].objects.filter(
                    schemecode=OuterRef("schemecode"),
                ).values("navrs")[:1]
            ))

        ordered_query = base_query.order_by(F("s_name").asc(nulls_last=True))
        result_query = ordered_query.values("schemecode", "s_name", "navrs")
        full_results = await sync_to_async(lambda: list(result_query))()
        

        if "frequency" in marker_to_models:
            frequency_model = marker_to_models["frequency"]
            sip_frequency_data = await sync_to_async(lambda: list(
                frequency_model.objects.filter(
                    schemecode__in=active_schemecodes
                ).values("schemecode", "frequency", "sip")
            ))()
            
            # Create a clean dictionary structure
            sip_frequency_map = {}
            for item in sip_frequency_data:
                schemecode = item["schemecode"]
                if schemecode not in sip_frequency_map:
                    sip_frequency_map[schemecode] = {}
                sip_frequency_map[schemecode][item["frequency"]] = item["sip"]
            
            # Add to results
            for item in full_results:
                item["SIP Availabilty with Frequency"] = sip_frequency_map.get(item["schemecode"], {})

        response.status_code=200
        return MFOptionandDetailsResponse(
            status=True,
            message="Mutual funds options and its details feteched successfully",
            data=full_results,
            status_code=response.status_code,
        )
    
    except Exception as e:
        response.status_code=400
        return MFOptionandDetailsResponse(
            status=False,
            message=f"Error occurred: {str(e)}",
            data=[],
            status_code=response.status_code,
        )
    
# @router.get("/mf_portfolio_section_real", response_model=PortfolioResponse)
# async def get_real_portfolio(
#         response : Response,
#         request : RealPortfolio,
#         Authorization: str = Header(),
#     ):

#     try:
#         decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)
#         email = decoded_payload.get("email")
#         mobile_number = decoded_payload.get("mobile_number")

#         if not any([email, mobile_number]):
#             response.status_code = 422
#             return MFOptionandDetailsResponse(
#                 status=False,
#                 message="Invalid JWT token: no email or mobile number found.",
#                 data=[],
#                 status_code=422,
#             )

#         if email:
#             user_id = await sync_to_async(
#                 UserContactInfo.objects.filter(email=email).first
#             )()
#         else:
#             user_id = await sync_to_async(
#                 UserContactInfo.objects.filter(mobile_number=mobile_number).first
#             )()

#         if not user_id:
#             response.status_code = 400
#             return MFOptionandDetailsResponse(
#                 status=False,
#                 message="User not found",
#                 data=[],
#                 status_code=400,
#             )
        
#         portfolios = await sync_to_async(lambda: list(
#             RealPortfolio.objects.filter(user_id=user_id)
#         ))()
#         if not portfolios:
#             response.status_code = 400
#             return PortfolioResponse(
#                 status=False,
#                 message="User Don't Have any Portfolio yet",
#                 data = [],
#                 status_code = response.status_code
#             )
#         data = []
#         for portfolio in portfolios:
#             current_value = portfolio.latest_nav * portfolio.quantity
#             returns_amount = current_value - portfolio.invested_amount
#             returns_percentage = returns_amount / portfolio.invested_amount * 100 if portfolio.invested_amount else 0.00

#             data.append({
#                 "fund_name": portfolio.mutual_fund,
#                 "fund_type": portfolio.fund_type,
#                 "fund_cap": portfolio.fund_cap,
#                 "investment_date": portfolio.investment_date,
#                 "invested_amount": portfolio.invested_amount,
#                 "quantity": portfolio.quantity,
#                 "current_value": round(current_value, 2),
#                 "returns_percentage": round(returns_percentage,2),
#                 "returns_amount": round(returns_amount, 2),
#             })

#         response.status_code = 200
#         return PortfolioResponse(
#             status=True,
#             message="Real portfolio fetched successfully",
#             data=data,
#             status_code=response.status_code
#         )

#     except Exception as e:
#         return PortfolioResponse(
#             status=False,
#             message=f"An unexpected error occurred: {str(e)}",
#             data={},
#             status_code=500,
#         )