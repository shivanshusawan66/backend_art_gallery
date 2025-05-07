import logging
from itertools import chain

from typing import Optional
from asgiref.sync import sync_to_async
from fastapi import APIRouter, Query, Response, Request

from django.db.models import OuterRef, Subquery, Sum
from django.apps import apps

from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.config.v1.api_config import api_config

from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable
from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *


from ai_mf_backend.models.v1.api.display_each_mf import (
    AbsoluteAndAnnualisedReturn,
    FundCategoryandSubcategory,
    FundDescriptionDetails,
    FundManagerDetails,
    FundOverview,
    FundRiskStatistics,
    MutualFundDashboardMobileResponse,
    MutualFundDashboardPayload,
    ReturnsCalculator,
    AssetAllocation,
    TopHolding,
    TopSector,
    MutualFundDashboardResponse,
    MutualFundFilterResponse,
    NavHistory,
    MutualFundDashboardErrorResponse,
)

router = APIRouter(tags=["mf_data"])

logger = logging.getLogger(__name__)


@router.get("/mf_fund_dashboard/")
@limiter.limit(api_config.REQUEST_PER_MIN)
async def get_fund_dashboard(
    request: Request,
    response: Response,
    is_mobile: Optional[bool] = Query(default=False, description="Is mobile?"),
    schemecode: Optional[int] = Query(
        default=None, description="data on the basis of schemecode"
    ),
):
    try:

        all_markers = list(
            set(chain.from_iterable(api_config.COMPONENT_MARKER_MAP.values()))
        )
        refs = await sync_to_async(
            lambda: list(MFReferenceTable.objects.filter(marker_name__in=all_markers))
        )()
        marker_to_models = {
            ref.marker_name: apps.get_model(api_config.PROJECT_NAME, ref.table_name)
            for ref in refs
            if ref.marker_name in all_markers
        }

        all_markers = list(
            set(
                ("navrs" if marker == "navrs_current" else marker)
                for marker in chain.from_iterable(
                    api_config.COMPONENT_MARKER_MAP.values()
                )
                if marker not in {"navrs_historical", "mode"}
            )
        )

        active_schemecodes = await sync_to_async(
            lambda: set(
                marker_to_models["status"]
                .objects.filter(status="Active")
                .values_list("schemecode", flat=True)
            )
        )()

        # check whether scheme is active or not
        if schemecode is not None and schemecode not in active_schemecodes:
            response.status_code = 404
            return MutualFundFilterResponse(
                status=False,
                message="this is not active schemecode",
                data=[],
                page=0,
                total_pages=0,
                total_data=0,
                status_code=response.status_code,
            )

        base_query = MFSchemeMasterInDetails.objects.filter(
            schemecode__in=active_schemecodes
        )

        # for category and subcategory filtering
        if "asset_type" in marker_to_models:
            base_query = base_query.annotate(
                asset_type=Subquery(
                    marker_to_models["asset_type"]
                    .objects.filter(classcode=OuterRef("classcode"))
                    .values("asset_type")[:1]
                )
            )
        if "category" in marker_to_models:
            base_query = base_query.annotate(
                category=Subquery(
                    marker_to_models["category"]
                    .objects.filter(classcode=OuterRef("classcode"))
                    .values("category")[:1]
                )
            )

        if "jalpha_y" in marker_to_models:
            base_query = base_query.annotate(
                jalpha_y=Subquery(
                    marker_to_models["jalpha_y"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("jalpha_y")[:1]
                )
            )

        if "treynor_y" in marker_to_models:
            base_query = base_query.annotate(
                treynor_y=Subquery(
                    marker_to_models["treynor_y"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("treynor_y")[:1]
                )
            )

        if "beta_y" in marker_to_models:
            base_query = base_query.annotate(
                beta_y=Subquery(
                    marker_to_models["beta_y"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("beta_y")[:1]
                )
            )

        if "sd_y" in marker_to_models:
            base_query = base_query.annotate(
                sd_y=Subquery(
                    marker_to_models["sd_y"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("sd_y")[:1]
                )
            )

        if "sharpe_y" in marker_to_models:
            base_query = base_query.annotate(
                sharpe_y=Subquery(
                    marker_to_models["sharpe_y"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("sharpe_y")[:1]
                )
            )

        if "_1yrret" in marker_to_models:
            base_query = base_query.annotate(
                _1yrret=Subquery(
                    marker_to_models["_1yrret"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_1yrret")[:1]
                )
            )

        if "_3yearret" in marker_to_models:
            base_query = base_query.annotate(
                _3yearret=Subquery(
                    marker_to_models["_3yearret"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_3yearret")[:1]
                )
            )

        if "_5yearret" in marker_to_models:
            model = marker_to_models["_5yearret"]
            base_query = base_query.annotate(
                _5yearret=Subquery(
                    model.objects.filter(schemecode=OuterRef("schemecode")).values(
                        "_5yearret"
                    )[:1]
                )
            )
        if "expratio" in marker_to_models:
            base_query = base_query.annotate(
                expratio=Subquery(
                    marker_to_models["expratio"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("expratio")[:1]
                )
            )

        if "navrs_current" in marker_to_models:
            base_query = base_query.annotate(
                navrs=Subquery(
                    marker_to_models["navrs_current"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("navrs")[:1]
                ),
                navdate=Subquery(
                    marker_to_models["navrs_current"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("navdate")[:1]
                ),
            )

        if "compname" in marker_to_models:
            model = marker_to_models["compname"]
            base_query = base_query.annotate(
                compname=Subquery(
                    model.objects.filter(schemecode=OuterRef("schemecode")).values(
                        "compname"
                    )[:1]
                ),
                sect_name=Subquery(
                    model.objects.filter(schemecode=OuterRef("schemecode")).values(
                        "sect_name"
                    )[:1]
                ),
                holdpercentage=Subquery(
                    model.objects.filter(schemecode=OuterRef("schemecode")).values(
                        "holdpercentage"
                    )[:1]
                ),
            )

        if "ShortSchemeDescrip" in marker_to_models:
            base_query = base_query.annotate(
                ShortSchemeDescrip=Subquery(
                    marker_to_models["ShortSchemeDescrip"]
                    .objects.filter(Schemecode=OuterRef("schemecode"))
                    .values("ShortSchemeDescrip")[:1]
                )
            )

        if "LongSchemeDescrip" in marker_to_models:
            base_query = base_query.annotate(
                LongSchemeDescrip=Subquery(
                    marker_to_models["LongSchemeDescrip"]
                    .objects.filter(Schemecode=OuterRef("schemecode"))
                    .values("LongSchemeDescrip")[:1]
                )
            )

        # For annualised and absolute return
        if "_1yrret_absolute" in marker_to_models:
            base_query = base_query.annotate(
                _1yrret_absolute=Subquery(
                    marker_to_models["_1yrret_absolute"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_1yrret")[:1]
                )
            )
        if "_3yearret_absolute" in marker_to_models:
            base_query = base_query.annotate(
                _3yearret_absolute=Subquery(
                    marker_to_models["_3yearret_absolute"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_3yearret")[:1]
                )
            )
        if "_5yearret_absolute" in marker_to_models:
            base_query = base_query.annotate(
                _5yearret_absolute=Subquery(
                    marker_to_models["_5yearret_absolute"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_5yearret")[:1]
                )
            )
        if "_1yrret_annualised" in marker_to_models:
            base_query = base_query.annotate(
                _1yrret_annualised=Subquery(
                    marker_to_models["_1yrret_annualised"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_1yrret")[:1]
                )
            )
        if "_3yearret_annualised" in marker_to_models:
            base_query = base_query.annotate(
                _3yearret_annualised=Subquery(
                    marker_to_models["_3yearret_annualised"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_3yearret")[:1]
                )
            )
        if "_5yearret_annualised" in marker_to_models:
            base_query = base_query.annotate(
                _5yearret_annualised=Subquery(
                    marker_to_models["_5yearret_annualised"]
                    .objects.filter(schemecode=OuterRef("schemecode"))
                    .values("_5yearret")[:1]
                )
            )

        # NAV history
        nav_history_data = []
        if "navrs_historical" in marker_to_models and schemecode is not None:
            nav_history_data = await sync_to_async(
                lambda: list(
                    marker_to_models["navrs_historical"]
                    .objects.filter(schemecode=schemecode)
                    .order_by("navdate")
                    .values("navdate", "navrs")
                )
            )()

        # When schemecode is provided, return detailed dashboard
        if schemecode is not None:
            result = await sync_to_async(
                lambda: base_query.filter(schemecode=schemecode)
                .values(*all_markers,'s_name')
                .first()
            )()

            manager_codes_qs = await sync_to_async(
                lambda: MFSchemeMasterInDetails.objects.filter(schemecode=schemecode)
                .values_list(
                    "fund_mgr_code1",
                    "FUND_MGR_CODE2",
                    "FUND_MGR_CODE3",
                    "FUND_MGR_CODE4",
                )
                .first()
            )()

            manager_codes = [code for code in manager_codes_qs if code is not None]

            manager_data = await sync_to_async(
                lambda: list(
                    MFFundManagerMaster.objects.filter(id__in=manager_codes).values(
                        "initial",
                        "fundmanager",
                        "qualification",
                        "basicdetails",
                        "experience",
                        "designation",
                        "age",
                    )
                )
            )()

            fund_managers = []
            for manager in manager_data:
                fund_manager = FundManagerDetails(
                    initial=manager.get("initial"),
                    fundmanager=manager.get("fundmanager"),
                    qualification=manager.get("qualification"),
                    basicdetails=manager.get("basicdetails"),
                    experience=manager.get("experience"),
                    designation=manager.get("designation"),
                    age=manager.get("age"),
                )
                fund_managers.append(fund_manager)

            sector_model = marker_to_models["sect_name"]
            sector_holding = await sync_to_async(
                lambda: list(
                    sector_model.objects.filter(schemecode=schemecode)
                    .values("sect_name")
                    .annotate(total_weight=Sum("holdpercentage"))
                )
            )()

            company_holdings_model = marker_to_models["compname"]
            company_holdings = await sync_to_async(
                lambda: list(
                    company_holdings_model.objects.filter(schemecode=schemecode)
                    .values("compname")
                    .annotate(total_weight=Sum("holdpercentage"))
                )
            )()

            if not company_holdings:
                top_holdings = []
            else:
                top_holdings_sorted = sorted(
                    company_holdings, key=lambda x: x["total_weight"], reverse=True
                )
                top_holdings = [
                    TopHolding(
                        holding_name=(
                            entry["compname"]
                            if entry["compname"] is not None
                            else "Others"
                        ),
                        weight=entry["total_weight"],
                    )
                    for entry in top_holdings_sorted
                ]

            if not sector_holding:
                top_sectors = []
            else:
                top_sectors_sorted = sorted(
                    sector_holding, key=lambda x: x["total_weight"], reverse=True
                )
                top_sectors = [
                    TopSector(
                        sector_name=(
                            entry["sect_name"]
                            if entry["sect_name"] is not None
                            else "Others"
                        ),
                        weight=entry["total_weight"],
                    )
                    for entry in top_sectors_sorted
                ]
            asset_allocation = None
            portfolio_qs = None
            if "mode" in marker_to_models and schemecode is not None:
                portfolio_qs = MFPortfolio.objects.filter(schemecode=schemecode)

            if await sync_to_async(portfolio_qs.exists)():
                cap_base_query = portfolio_qs.annotate(
                    mode=Subquery(
                        marker_to_models["mode"]
                        .objects.filter(fincode=OuterRef("fincode"))
                        .values("mode")[:1]
                    )
                )
                mode_data = await sync_to_async(
                    lambda: list(
                        cap_base_query.values("mode").annotate(
                            mode_percentage=Sum("holdpercentage")
                        )
                    )
                )()
                for entry in mode_data:
                    allocation = {
                        entry["mode"]: entry["mode_percentage"] for entry in mode_data
                    }

                asset_allocation = AssetAllocation(
                    large_cap_percent=allocation.get("Large Cap"),
                    mid_cap_percent=allocation.get("Mid Cap"),
                    small_cap_percent=allocation.get("Small Cap"),
                    others_cap_percentage=allocation.get(None),
                )

            else:
                asset_allocation = AssetAllocation(
                    large_cap_percent=None,
                    mid_cap_percent=None,
                    small_cap_percent=None,
                    others_cap_percentage=None,
                )

            response.status_code = 200
            if is_mobile:
                return MutualFundDashboardMobileResponse(
                    status=True,
                    message="Success",
                    status_code=response.status_code,
                    data=MutualFundDashboardPayload(

                        s_name=result.get('s_name'),
                        fund_category_subcategory=FundCategoryandSubcategory(
                            fund_category=result.get("asset_type"),
                            fund_subcategory=result.get("category"),
                        ),
                        fund_overview=FundOverview(
                            net_assets_value=result.get("navrs"),
                            three_year_return=result.get("_3yearret"),
                            five_year_return=result.get("_5yearret"),
                            expense_ratio=result.get("expratio"),
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
                        fund_manager_details=fund_managers,
                        fund_description=FundDescriptionDetails(
                            short_description=result.get("ShortSchemeDescrip"),
                            long_description=result.get("LongSchemeDescrip"),
                        ),
                        absolute_and_annualised_return=AbsoluteAndAnnualisedReturn(
                            absolute_1yr_return=result.get("_1yrret_absolute"),
                            absolute_3yr_return=result.get("_3yearret_absolute"),
                            absolute_5yr_return=result.get("_5yearret_absolute"),
                            annualised_1_yr_return=result.get("_1yrret_annualised"),
                            annualised_3_yr_return=result.get("_3yearret_annualised"),
                            annualised_5yr_return=result.get("_5yearret_annualised"),
                        ),
                        fund_history_nav=NavHistory(
                            data=nav_history_data,
                        ),
                    ),
                )
            else:
                return MutualFundDashboardResponse(
                    status=True,
                    message="Success",
                    s_name=result.get('s_name'),
                    status_code=response.status_code,
                    fund_category_subcategory=FundCategoryandSubcategory(
                        fund_category=result.get("asset_type"),
                        fund_subcategory=result.get("category"),
                    ),
                    fund_overview=FundOverview(
                        net_assets_value=result.get("navrs"),
                        three_year_return=result.get("_3yearret"),
                        five_year_return=result.get("_5yearret"),
                        expense_ratio=result.get("expratio"),

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
                    fund_manager_details=fund_managers,
                    fund_description=FundDescriptionDetails(
                        short_description=result.get("ShortSchemeDescrip"),
                        long_description=result.get("LongSchemeDescrip"),
                    ),
                    absolute_and_annualised_return=AbsoluteAndAnnualisedReturn(
                        absolute_1yr_return=result.get("_1yrret_absolute"),
                        absolute_3yr_return=result.get("_3yearret_absolute"),
                        absolute_5yr_return=result.get("_5yearret_absolute"),
                        annualised_1_yr_return=result.get("_1yrret_annualised"),
                        annualised_3_yr_return=result.get("_3yearret_annualised"),
                        annualised_5yr_return=result.get("_5yearret_annualised"),
                    ),
                    fund_history_nav=NavHistory(
                        data=nav_history_data,
                    ),
                )
        else:
            response.status_code = 404
            return MutualFundDashboardErrorResponse(
                status=False,
                message="Please Provide schemecode",
                data=[],
                status_code=response.status_code,
            )

    except Exception as e:
        response.status_code = 400
        logger.error(f"Error processing request: {str(e)}")
        return MutualFundDashboardErrorResponse(
            status=False,
            message=f"Error occurred: {str(e)}",
            data=[],
            status_code=response.status_code,
        )