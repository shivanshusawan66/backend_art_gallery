from datetime import date
import logging
from typing import Optional

from asgiref.sync import sync_to_async
from django.apps import apps
from django.db.models import OuterRef, Subquery, F
from fastapi import APIRouter, Query, Response, Depends, Request, status, Header

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.utils.v1.authentication.secrets import (
    login_checker,
    validate_user_id,
)

from ai_mf_backend.models.v1.database.mf_master_data import MFSchemeClassMaster, MFSchemeMasterInDetails
from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable

from ai_mf_backend.models.v1.database.user_portfolio import (
    MFRealPortfolio,
    MFTrialPortfolio,
)
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import (
    MFNSEAssetValueLatest,
)

from ai_mf_backend.models.v1.api.user_portfolio import (
    GetPortfolioResponse,
    DeletePortfolioRequest,
    DeletePortfolioResponse,
    AddPortfolioRequest,
    AddPortfolioResponse,
    PatchPortfolioRequest,
    PatchPortfolioResponse,
    MFOptionandDetailsResponse,
)


from ai_mf_backend.config.v1.api_config import api_config

router = APIRouter()
logger = logging.getLogger(__name__)



@router.get(
    "/get_mf_options_and_details",
    response_model=MFOptionandDetailsResponse,
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def get_mf_options_and_details(
    request: Request,
    response: Response,
    fund_name: Optional[str] = Query(
        default=None, description="Search mutual fund name"
    ),
    investment_date: Optional[date] = Query(
        default=None, description="Investment date in YYYY-MM-DD format"
    ),
):
    try:
        marker_list = ["status", "s_name", "navrs_current", "navrs_historical","frequency", "sip"]

        refs = await sync_to_async(
            lambda: list(MFReferenceTable.objects.filter(marker_name__in=marker_list))
        )()

        marker_to_models = {
            ref.marker_name: apps.get_model(api_config.PROJECT_NAME, ref.table_name)
            for ref in refs
            if ref.marker_name in marker_list
        }

        active_schemecodes = await sync_to_async(
            lambda: set(
                marker_to_models["status"]
                .objects.filter(status="Active")
                .values_list("schemecode", flat=True)
            )
        )()

        base_query = MFSchemeMasterInDetails.objects.filter(
            schemecode__in=active_schemecodes
        )

        if fund_name:
            base_query = base_query.filter(s_name__icontains=fund_name)
        
        if investment_date == date.today():
            if "navrs_current" in marker_to_models:
                base_query = base_query.annotate(
                    navrs=Subquery(
                        marker_to_models["navrs_current"]
                        .objects.filter(
                            schemecode=OuterRef("schemecode"),
                            navdate__lte=investment_date,
                        )
                        .order_by("-navdate")
                        .values("navrs")[:1]
                    )
                )
        else:
            if "navrs_historical" in marker_to_models:
                base_query = base_query.annotate(
                    navrs=Subquery(
                        marker_to_models["navrs_historical"]
                        .objects.filter(
                            schemecode=OuterRef("schemecode"),
                            navdate__lte=investment_date,
                        )
                        .order_by("-navdate")
                        .values("navrs")[:1]
                    )
                )

        ordered_query = base_query.order_by(F("s_name").asc(nulls_last=True))
        result_query = ordered_query.values("schemecode", "s_name", "navrs")
        full_results = await sync_to_async(lambda: list(result_query))()

        if "frequency" in marker_to_models:
            frequency_model = marker_to_models["frequency"]
            sip_frequency_data = await sync_to_async(
                lambda: list(
                    frequency_model.objects.filter(
                        schemecode__in=active_schemecodes
                    ).values("schemecode", "frequency", "sip")
                )
            )()

            # Create a clean dictionary structure
            sip_frequency_map = {}
            for item in sip_frequency_data:
                schemecode = item["schemecode"]
                if schemecode not in sip_frequency_map:
                    sip_frequency_map[schemecode] = {}
                sip_frequency_map[schemecode][item["frequency"]] = item["sip"]

            # Add to results
            for item in full_results:
                item["SIP_Availabilty_with_Frequency"] = sip_frequency_map.get(
                    item["schemecode"], {}
                )

        response.status_code = 200
        return MFOptionandDetailsResponse(
            status=True,
            message="Mutual funds options and its details feteched successfully",
            data=full_results,
            status_code=response.status_code,
        )

    except Exception as e:
        response.status_code = 400
        return MFOptionandDetailsResponse(
            status=False,
            message=f"Error occurred: {str(e)}",
            data=[],
            status_code=response.status_code,
        )

@router.get(
    "/mf_portfolio_section",
    response_model=GetPortfolioResponse,
    dependencies=[Depends(login_checker)],  # assuming login_checker is implemented elsewhere
    status_code=200,
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def mf_portfolio_section(
    request: Request,
    is_real: bool,
    response: Response,
    Authorization: str = Header(),
):
    try:
        user_instance = await validate_user_id(Authorization=Authorization)
        user_id = user_instance.user_id

        PortfolioModel = MFRealPortfolio if is_real else MFTrialPortfolio

        all_scheme_codes = await sync_to_async(list)(PortfolioModel.objects.filter(user_id=user_id).values_list("scheme_code", flat=True))

        base_qs = MFSchemeMasterInDetails.objects.filter(schemecode__in=all_scheme_codes)

        asset_type_sq = (
            MFSchemeClassMaster.objects
            .filter(classcode=OuterRef("classcode"))
            .values("asset_type")[:1]
        )
        category_sq = (
            MFSchemeClassMaster.objects
            .filter(classcode=OuterRef("classcode"))
            .values("category")[:1]
        )

        result_qs = base_qs.annotate(
            asset_type=Subquery(asset_type_sq),
            category=Subquery(category_sq),
        )

        # fetch as a list of dicts without blocking
        rows = await sync_to_async(list)(
            result_qs.values("schemecode", "asset_type", "category")
        )

        # now fold into one dict:
        scheme_map = {
            rec["schemecode"]: {
                "asset_type": rec["asset_type"],
                "category":   rec["category"],
            }
            for rec in rows
        }

        scheme_name_sq = (
            MFSchemeMasterInDetails.objects
            .filter(schemecode=OuterRef("scheme_code"))
            .values("s_name")[:1]
        )

        latest_nav_sq = (
            MFNSEAssetValueLatest.objects
            .filter(
                schemecode=OuterRef("scheme_code"),
            )
            .values("navrs")[:1]
        )

        qs = (
            PortfolioModel.objects
            .filter(user_id=user_id)
            .annotate(
                scheme_name=Subquery(scheme_name_sq),
                latest_fund_nav=Subquery(latest_nav_sq),
            )
        )

        portfolio_rows = await sync_to_async(list)(qs)

        real_portfolio_docs =  [
            Portfolio(
                investment_id=p.id,
                scheme_code=p.scheme_code,
                fund_name=p.scheme_name,
                fund_type     = scheme_map.get(p.scheme_code, {}).get('asset_type',None),
                fund_category = scheme_map.get(p.scheme_code, {}).get('category',None),
                investment_date=p.investment_date,
                invested_amount=p.invested_amount,
                quantity=p.quantity,
                frequency=p.frequency,
                investment_type=p.investment_type,
                current_fund_nav=p.latest_fund_nav,
            )
            for p in portfolio_rows
        ]

        return GetPortfolioResponse(
            status=True,
            message="Portfolio fetched successfully",
            data={"portfolios": real_portfolio_docs},
            status_code=response.status_code,
        )

    except Exception as e:
        logger.error(f"Error retrieving portfolio values: {str(e)}", exc_info=True)
        response_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.status_code = response_status_code
        return GetPortfolioResponse(
            status=False,
            message=f"Processing failed: {str(e)}",
            data={},
            status_code=response_status_code,
        )

    

@router.delete(
    "/delete_mf_portfolio_item",
    response_model=DeletePortfolioResponse,
    dependencies=[Depends(login_checker)],
    status_code=200,
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def delete_mf_portfolio_item(
    request: Request,
    body: DeletePortfolioRequest,
    response: Response,
    Authorization: str = Header(),
):
    try:
        user_instance = await validate_user_id(Authorization=Authorization)
        user_id = user_instance.user_id

        is_real = body.is_real
        investment_id = body.investment_id

        PortfolioModel = MFRealPortfolio if is_real else MFTrialPortfolio

        await sync_to_async(lambda: PortfolioModel.objects.filter(
            user_id=user_id, 
            id=investment_id
        ).delete())()

        return DeletePortfolioResponse(
            status=True,
            message="Successfully deleted the data for the given investment id",
            data={},
            status_code=response.status_code,
        )

    except Exception as e:
        logger.error(f"Error deleting investment id: {str(e)}", exc_info=True)
        response_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.status_code = response_status_code
        return DeletePortfolioResponse(
            status=False,
            message=f"Processing failed: {str(e)}",
            data={},
            status_code=response_status_code,
        )



@router.post(
    "/add_mf_portfolio_item",
    response_model=AddPortfolioResponse,
    dependencies=[Depends(login_checker)],
    status_code=200,
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def add_mf_portfolio_item(
    request:Request,
    body: AddPortfolioRequest,
    response: Response,
    Authorization: str = Header(),
):
    try:
        user_instance = await validate_user_id(Authorization=Authorization)

        is_real = body.is_real
        investments = body.investments

        PortfolioModel = MFRealPortfolio if is_real else MFTrialPortfolio
        instances = []
        for investment in investments:
            instances.append(PortfolioModel(
                user_id=user_instance,
                scheme_code=investment.scheme_code,
                current_fund_nav=investment.current_fund_nav,
                investment_date=investment.investment_date,
                investment_type=investment.investment_type,
                frequency=investment.frequency,
                invested_amount=investment.invested_amount,
                quantity=investment.quantity,
            )
        )
        await sync_to_async(PortfolioModel.objects.bulk_create)(instances)

        return AddPortfolioResponse(
            status=True,
            message="Successfully added the data for the given investment id",
            data={},
            status_code=response.status_code,
        )

    except Exception as e:
        logger.error(f"Error adding investment id: {str(e)}", exc_info=True)
        response_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.status_code = response_status_code
        return AddPortfolioResponse(
            status=False,
            message=f"Processing failed: {str(e)}",
            data={},
            status_code=response_status_code,
        )


@router.patch(
    "/patch_mf_portfolio_item",
    response_model=PatchPortfolioResponse,
    dependencies=[Depends(login_checker)],
    status_code=200,
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def patch_mf_portfolio_item(
    request: Request,
    body: PatchPortfolioRequest,
    response: Response,
    Authorization: str = Header(),
):
    try:
        user_instance = await validate_user_id(Authorization=Authorization)

        is_real = body.is_real
        investments = body.investments

        PortfolioModel = MFRealPortfolio if is_real else MFTrialPortfolio

        for investment in investments:
            sync_to_async(lambda: PortfolioModel.objects.filter(
                id=investment.investment_id,
                user_id=user_instance,
            ).update(
                latest_nav=investment.latest_nav,
                scheme_code=investment.scheme_code,
                fund_name=investment.fund_name,
                fund_type=investment.fund_type,
                fund_category=investment.fund_category,
                orig_fund_nav=investment.orig_fund_nav,
                investment_date=investment.investment_date,
                investment_type=investment.investment_type,
                frequency=investment.frequency,
                invested_amount=investment.invested_amount,
                quantity=investment.quantity,
            )
        )

        return PatchPortfolioResponse(
            status=True,
            message="Successfully added the data for the given investment id",
            data={},
            status_code=response.status_code,
        )

    except Exception as e:
        logger.error(f"Error adding investment id: {str(e)}", exc_info=True)
        response_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.status_code = response_status_code
        return PatchPortfolioResponse(
            status=False,
            message=f"Processing failed: {str(e)}",
            data={},
            status_code=response_status_code,
        )