import logging
from itertools import chain
from fastapi import APIRouter, Query, Response, Request
from typing import Optional
from asgiref.sync import sync_to_async
from django.db.models import OuterRef, Subquery
from django.apps import apps

from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.models.v1.api.display_each_mf import MutualFundFilterResponse
from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable
from ai_mf_backend.models.v1.database.mf_master_data import MFSchemeMasterInDetails, MFSchemeMaster
from ai_mf_backend.models.v1.database.mf_category_wise import MutualFundSubcategory, MutualFundType
from ai_mf_backend.models.v1.database.mf_filter_parameters import MFFilterParameters, MFFilterColors
from ai_mf_backend.core.v1.api import limiter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/mf_fund_filter/")
@limiter.limit(api_config.REQUEST_PER_MIN)
async def get_fund_filter(
    request: Request,
    response: Response,
    sort_by: Optional[int] = Query(None, description="MF sorted by given id"),
    risk: Optional[int] = Query(None, description="MF filtered by risk"),
    investment_type: Optional[bool] = Query(None, description="MF filter by investment_type"),
    fund_category_id: Optional[int] = Query(None),
    fund_subcategory_id: Optional[int] = Query(None),
    page: int = Query(1, gt=0),
    page_size: int = Query(api_config.DEFAULT_PAGE_SIZE, ge=1, le=api_config.MAX_PAGE_SIZE),
):
    try:
        filter_kwargs = {}

        if fund_category_id is not None:
            filter_kwargs["asset_type"] = await sync_to_async(
                lambda: MutualFundType.objects.filter(id=fund_category_id).values_list("fund_type", flat=True).first()
            )()

        if fund_subcategory_id is not None:
            filter_kwargs["category"] = await sync_to_async(
                lambda: MutualFundSubcategory.objects.filter(id=fund_subcategory_id).values_list("fund_subcategory", flat=True).first()
            )()

        order_field = None
        if sort_by is not None:
            order_field = await sync_to_async(
                lambda: MFFilterParameters.objects.filter(id=sort_by).values_list("parameter_name", flat=True).first()
            )()
            if not order_field:
                response.status_code = 400
                return MutualFundFilterResponse(
                    status=False,
                    message=f"No ordering field found for filter ID {sort_by}",
                    data=[],
                    page=0,
                    total_pages=0,
                    total_data=0,
                    status_code=400
                )

        risk_type = None
        if risk is not None:
            risk_type = await sync_to_async(
                lambda: MFFilterColors.objects.filter(id=risk).values_list("color_name", flat=True).first()
            )()
            filter_kwargs["color"] = risk_type
            if not risk_type:
                response.status_code = 400
                return MutualFundFilterResponse(
                    status=False,
                    message=f"No risk color found for color ID {risk}",
                    data=[],
                    page=0,
                    total_pages=0,
                    total_data=0,
                    status_code=400
                )

        all_fields = api_config.MUTUAL_FUND_DASHBOARD_COLOUMNS
        all_markers = list(set(chain.from_iterable(api_config.COMPONENT_MARKER_MAP.values())))

        refs = await sync_to_async(lambda: list(
            MFReferenceTable.objects.filter(marker_name__in=all_markers)
        ))()

        marker_to_models = {
            ref.marker_name: apps.get_model(api_config.PROJECT_NAME, ref.table_name)
            for ref in refs
        }

        # Get active schemecodes
        active_schemecodes = await sync_to_async(
            lambda: set(
                marker_to_models["status"]
                .objects
                .filter(status="Active")
                .values_list("schemecode", flat=True)
            )
        )()

        # Base query
        base_query = MFSchemeMasterInDetails.objects.filter(
            schemecode__in=active_schemecodes
        ).annotate(
            color=Subquery(
                MFSchemeMaster.objects.filter(schemecode=OuterRef("schemecode"))
                .values("color")[:1]
            )
        )

        # navrs and navdate
        if "navrs_current" in marker_to_models:
            base_query = base_query.annotate(
                navrs=Subquery(
                    marker_to_models["navrs_current"].objects
                    .filter(schemecode=OuterRef("schemecode"))
                    .values("navrs")[:1]
                ),
                navdate=Subquery(
                    marker_to_models["navrs_current"].objects
                    .filter(schemecode=OuterRef("schemecode"))
                    .values("navdate")[:1]
                )
            )

        # Risk metrics
        if "jalpha_y" in marker_to_models:
            base_query = base_query.annotate(
                jalpha_y=Subquery(
                    marker_to_models["jalpha_y"].objects
                    .filter(schemecode=OuterRef("schemecode"))
                    .values("jalpha_y")[:1]
                )
            )

        if "treynor_y" in marker_to_models:
            base_query = base_query.annotate(
                treynor_y=Subquery(
                    marker_to_models["treynor_y"].objects
                    .filter(schemecode=OuterRef("schemecode"))
                    .values("treynor_y")[:1]
                )
            )

        if "beta_y" in marker_to_models:
            base_query = base_query.annotate(
                beta_y=Subquery(
                    marker_to_models["beta_y"].objects
                    .filter(schemecode=OuterRef("schemecode"))
                    .values("beta_y")[:1]
                )
            )

        if "sd_y" in marker_to_models:
            base_query = base_query.annotate(
                sd_y=Subquery(
                    marker_to_models["sd_y"].objects
                    .filter(schemecode=OuterRef("schemecode"))
                    .values("sd_y")[:1]
                )
            )

        if "sharpe_y" in marker_to_models:
            base_query = base_query.annotate(
                sharpe_y=Subquery(
                    marker_to_models["sharpe_y"].objects
                    .filter(schemecode=OuterRef("schemecode"))
                    .values("sharpe_y")[:1]
                )
            )

    
        if "_1yrret" in marker_to_models:
            base_query = base_query.annotate(
                _1yrret=Subquery(
                    marker_to_models["_1yrret"].objects
                    .filter(schemecode=OuterRef("schemecode"))
                    .values("_1yrret")[:1]
                )
            )

        if "_3yearret" in marker_to_models:
            base_query = base_query.annotate(
                _3yearret=Subquery(
                    marker_to_models["_3yearret"].objects
                    .filter(schemecode=OuterRef("schemecode"))
                    .values("_3yearret")[:1]
                )
            )

        if "_5yearret" in marker_to_models:
            base_query = base_query.annotate(
                _5yearret=Subquery(
                    marker_to_models["_5yearret"].objects
                    .filter(schemecode=OuterRef("schemecode"))
                    .values("_5yearret")[:1]
                )
            )

        # Classification fields
        if "asset_type" in marker_to_models:
            base_query = base_query.annotate(
                asset_type=Subquery(
                    marker_to_models["asset_type"].objects
                    .filter(classcode=OuterRef("classcode"))
                    .values("asset_type")[:1]
                )
            )

        if "category" in marker_to_models:
            base_query = base_query.annotate(
                category=Subquery(
                    marker_to_models["category"].objects
                    .filter(classcode=OuterRef("classcode"))
                    .values("category")[:1]
                )
            )

        if investment_type is not None:
            filter_kwargs['sip'] = sip='T' if investment_type else 'F'

        result_query = base_query.filter(**filter_kwargs).values(*all_fields,'schemecode').order_by(order_field)

        total_count = await sync_to_async(result_query.count)()
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = await sync_to_async(lambda: list(result_query[start_idx:end_idx]))()
        total_pages = (total_count + page_size - 1) // page_size

        if not paginated:
            response.status_code = 404
            return MutualFundFilterResponse(
                status=False,
                message="No data found",
                data=[],
                page=0,
                total_pages=0,
                total_data=0,
                status_code=404
            )

        response.status_code = 200
        return MutualFundFilterResponse(
            status=True,
            message="Successfully retrieved MF data",
            data=paginated,
            page=page,
            total_pages=total_pages,
            total_data=total_count,
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        response.status_code = 400
        return MutualFundFilterResponse(
            status=False,
            message=f"Error occurred: {e}",
            data=[],
            page=0,
            total_pages=0,
            total_data=0,
            status_code=400
        )
