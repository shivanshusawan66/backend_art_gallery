import logging
import warnings
from fastapi import APIRouter, Query, Response, status, Request
from typing import List, Optional
from asgiref.sync import sync_to_async
from django.db.models import OuterRef, Subquery, F, Sum
from django.apps import apps
from itertools import chain
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable
from ai_mf_backend.core.v1.api import limiter
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *
from ai_mf_backend.models.v1.database.mf_category_wise import(MutualFundSubcategory,MutualFundType)
from ai_mf_backend.utils.v1.api_projection.valid_fields import process_fields
from ai_mf_backend.models.v1.api.display_each_mf import (
    FundOverview, FundRiskStatistics, ReturnsCalculator, AssetAllocation,
    TopHolding, TopSector, MutualFundDashboardResponse, MutualFundFilterResponse,
    NavHistory
)

router = APIRouter()

logger = logging.getLogger(__name__)

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/mf_fund_dashboard")
async def get_fund_dashboard(
    request: Request,
    response: Response,
    fields: Optional[str] = Query(default=None, description="Comma-separated list of fields to include"),
    schemecode: Optional[int] = Query(default=None, description="data on the basis of schemecode"),
    fund_category_id: Optional[int] = Query(default=None),
    fund_subcategory_id: Optional[int] = Query(default=None),
    page: int = Query(1, gt=0),
    page_size: int = Query(api_config.DEFAULT_PAGE_SIZE, ge=1, le=api_config.MAX_PAGE_SIZE),
):
    try:
       

        COMPONENT_MARKER_MAP = {
            "Fund Risk": ["jalpha_y", "beta_y", "_1yrret", "treynor_y", "sd_y", "sharpe_y", "status"],
            "Fund Overview": [ "_5yearret","_3yearret","navrs_current"],
            "Return Calculator": ["sip"],
            "Asset Allocation": ["compname", "sect_name", "holdpercentage", "mode"],
            "Historical Nav & Returns": ["navrs_historical"],
            "Extra":["asset_type","mode","category"],
        }
        
        FILTER_FIELD_MAPPING = {       
        "return":  ["_5yearret","_3yearret","_1yrret"],
        "risk": ["sd_y", "beta_y", "sharpe_y","treynor_y","jalpha_y"],  
        "investment_type":["sip"],
        }


        

        filter_kwargs = {}

        if fund_category_id:
            filter_kwargs["asset_type"] = await sync_to_async(
                lambda: MutualFundType.objects.filter(id=fund_category_id)
                .values_list("fund_type", flat=True)
                .first()
            )()

        if fund_subcategory_id:
            filter_kwargs["category"] = await sync_to_async(
                lambda: MutualFundSubcategory.objects.filter(id=fund_subcategory_id)
                .values_list("fund_subcategory", flat=True)
                .first()
            )()

          

        all_fields = api_config.MUTUAL_FUND_DASHBOARD_COLOUMNS
        if fields is not None:
          fields_to_project = process_fields(",".join(FILTER_FIELD_MAPPING[fields]), all_fields)


        all_markers = list(set(chain.from_iterable(COMPONENT_MARKER_MAP.values())))
      
        refs = await sync_to_async(lambda: list(MFReferenceTable.objects.filter(marker_name__in=all_markers)))()
        marker_to_models = {
            ref.marker_name: apps.get_model(api_config.PROJECT_NAME, ref.table_name)
            for ref in refs if ref.marker_name in all_markers
        }
        
        all_markers = list(
            set(
                "navrs" if marker == "navrs_current" else marker
                for marker in chain.from_iterable(COMPONENT_MARKER_MAP.values())
                if marker not in {"navrs_historical", "mode"}
               )
            )


        active_schemecodes = await sync_to_async(
            lambda: set(marker_to_models['status'].objects.filter(status="Active").values_list("schemecode", flat=True))
        )()

        if schemecode is not None and schemecode not in active_schemecodes:
            response.status_code = 404
            return MutualFundFilterResponse(
                status=False,
                message="this is not active schemecode",
                data=[],
                page=0,
                total_pages=0,
                total_data=0,
                status_code=response.status_code
            )

        base_query = MFSchemeMasterInDetails.objects.filter(schemecode__in=active_schemecodes)

        if "asset_type" in marker_to_models:
            base_query = base_query.annotate(
                asset_type=Subquery(
                    marker_to_models["asset_type"].objects.filter(classcode=OuterRef("classcode")).values("asset_type")[:1]
                )
            )
        if "category" in marker_to_models:
            base_query = base_query.annotate(
                category=Subquery(
                    marker_to_models["category"].objects.filter(classcode=OuterRef("classcode")).values("category")[:1]
                )
            )

        

        if "jalpha_y" in marker_to_models:
            base_query = base_query.annotate(
                jalpha_y=Subquery(marker_to_models["jalpha_y"].objects.filter(schemecode=OuterRef("schemecode")).values("jalpha_y")[:1])
            )

        if "treynor_y" in marker_to_models:
            base_query = base_query.annotate(
                treynor_y=Subquery(marker_to_models["treynor_y"].objects.filter(schemecode=OuterRef("schemecode")).values("treynor_y")[:1])
            )

        if "beta_y" in marker_to_models:
            base_query = base_query.annotate(
                beta_y=Subquery(marker_to_models["beta_y"].objects.filter(schemecode=OuterRef("schemecode")).values("beta_y")[:1])
            )

        if "sd_y" in marker_to_models:
            base_query = base_query.annotate(
                sd_y=Subquery(marker_to_models["sd_y"].objects.filter(schemecode=OuterRef("schemecode")).values("sd_y")[:1])
            )

        if "sharpe_y" in marker_to_models:
            base_query = base_query.annotate(
                sharpe_y=Subquery(marker_to_models["sharpe_y"].objects.filter(schemecode=OuterRef("schemecode")).values("sharpe_y")[:1])
            )
        
        if "_1yrret" in marker_to_models:
            base_query = base_query.annotate(
                _1yrret=Subquery(
                    marker_to_models["_1yrret"].objects.filter(schemecode=OuterRef("schemecode")).values("_1yrret")[:1]
                )
            )
        
        if "_3yearret" in marker_to_models:
            base_query = base_query.annotate(
                _3yearret=Subquery(
                    marker_to_models["_3yearret"].objects.filter(schemecode=OuterRef("schemecode")).values("_3yearret")[:1]
                )
            )
        
        if "_5yearret" in marker_to_models:
            model = marker_to_models["_5yearret"]
            base_query = base_query.annotate(
                _5yearret=Subquery(model.objects.filter(schemecode=OuterRef("schemecode")).values("_5yearret")[:1])
            )

        if "navrs_current" in marker_to_models:
            base_query = base_query.annotate(
                navrs=Subquery(
                    marker_to_models["navrs_current"].objects.filter(schemecode=OuterRef("schemecode")).values("navrs")[:1]
                ),
                navdate=Subquery(
                    marker_to_models["navrs_current"].objects.filter(schemecode=OuterRef("schemecode")).values("navdate")[:1]
                )
            )

        if "compname" in marker_to_models:
            model = marker_to_models["compname"]
            base_query = base_query.annotate(
                compname=Subquery(model.objects.filter(schemecode=OuterRef("schemecode")).values("compname")[:1]),
                sect_name=Subquery(model.objects.filter(schemecode=OuterRef("schemecode")).values("sect_name")[:1]),
                holdpercentage=Subquery(model.objects.filter(schemecode=OuterRef("schemecode")).values("holdpercentage")[:1]),
            )

        # NAV history
        nav_history_data  = []
        if "navrs_historical" in marker_to_models and schemecode is not None:
            nav_history_data = await sync_to_async(
                lambda: list(
                    marker_to_models["navrs_historical"].objects.filter(schemecode=schemecode)
                    .order_by("navdate")
                    .values("navdate", "navrs")
                )
            )()

        # Asset allocation
        asset_allocation = None
        if "mode" in marker_to_models and schemecode is not None:
            cap_base_query = MFPortfolio.objects.filter(schemecode=schemecode).annotate(
                mode=Subquery(marker_to_models["mode"].objects.filter(fincode=OuterRef("fincode")).values("mode")[:1])
            )
    
            mode_data = await sync_to_async(
                lambda: list(
                    cap_base_query.values("mode").annotate(mode_percentage=Sum("holdpercentage"))
                )
            )()

            for entry in mode_data:
                allocation = {entry["mode"]: entry["mode_percentage"] for entry in mode_data}
            
            asset_allocation = AssetAllocation(
                large_cap_percent=allocation.get("Large Cap"),
                mid_cap_percent=allocation.get("Mid Cap"),
                small_cap_percent=allocation.get("Small Cap"),
                others_cap_percentage = allocation.get(None)
            )

        # When schemecode is provided, return detailed dashboard
        if schemecode is not None and not fields:
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
                        
       
            # Execute query with adjusted markers
            result = await sync_to_async(
                lambda: base_query.filter(schemecode=schemecode).values(*all_markers).first()
            )()

            sector_model = marker_to_models["sect_name"]
            sector_holding = await sync_to_async(lambda: list(
                sector_model.objects.filter(schemecode=schemecode).values("sect_name").annotate(total_weight=Sum("holdpercentage"))
            ))()

            holding_model = marker_to_models["compname"]
            company_holdings = await sync_to_async(lambda: list(
                holding_model.objects.filter(schemecode=schemecode).values("compname").annotate(total_weight=Sum("holdpercentage"))
            ))()

            top_holdings_sorted = sorted(company_holdings, key=lambda x: x["total_weight"], reverse=True)
            top_holdings = [
                TopHolding(holding_name=entry["compname"], weight=entry["total_weight"])
                for entry in top_holdings_sorted[0:5]
            ]

            top_sectors_sorted = sorted(sector_holding, key=lambda x: x["total_weight"], reverse=True)
            top_sectors = [
                TopSector(sector_name=entry["sect_name"], weight=entry["total_weight"])
                for entry in top_sectors_sorted[0:5]
            ]
     
            response.status_code = 200
            return MutualFundDashboardResponse(
                status=True,
                message="Success",
                status_code=response.status_code,
                fund_history_nav=NavHistory(
                    data=nav_history_data,  
                    
                ),
                fund_overview=FundOverview(
                    net_assets_value=result.get("navrs"),
                    three_year_return=result.get("_3yearret"),
                    five_year_return=result.get("_5yearret"),
                ),
                fund_risk_statistics=FundRiskStatistics(
                    one_year_return=result.get("_1yrret"),
                    sharpe_ratio=result.get("sharpe_y"),
                    std_dev=result.get("sd_y"),
                    beta=result.get("beta_y"),
                    jalpha=result.get("jalpha_y"),
                    treynor=result.get("treynor_y"),
                ),
                returns_calculator=ReturnsCalculator(sip=result.get("sip")),
                asset_allocation=asset_allocation,
                top_holdings=top_holdings,
                top_sectors=top_sectors,
            )

        # When filtering with fields
        elif not schemecode and fields is not None:
            if fields == "return":     
                result_query = base_query.filter(**filter_kwargs).values(*fields_to_project, 's_name')

            if fields=="risk":
                result_query = base_query.filter(**filter_kwargs).values(*fields_to_project,'s_name')

            if fields=="investment_type":
                result_query = base_query.filter(**filter_kwargs).values(*fields_to_project,'s_name')
                

            total_count = await sync_to_async(result_query.count)()
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_results = await sync_to_async(lambda: list(result_query[start_idx:end_idx]))()
            total_page = (total_count + page_size - 1) // page_size

            response.status_code = 200
            return MutualFundFilterResponse(
                status=True,
                message="Successfully filtered the mf data",
                data=paginated_results,
                page=page,
                total_pages=total_page,
                total_data=total_count,
                status_code=response.status_code ,
            )
        
        response.status_code = 404
        return MutualFundFilterResponse(
            status=False,
            message="No data found",
            data=[],
            page=0,
            total_pages=0,
            total_data=0,
            status_code=response.status_code
        )

    except Exception as e:
        response.status_code = 400
        logger.error(f"Error processing request: {str(e)}")
        return MutualFundFilterResponse(
            status=False,
            message=f"Error occurred: {str(e)}",
            data=[],
            page=0,
            total_pages=0,
            total_data=0,
            status_code=response.status_code,
        )
