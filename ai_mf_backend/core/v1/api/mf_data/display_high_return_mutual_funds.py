from fastapi import APIRouter, Query, Response, status, Request
from typing import List, Optional
from asgiref.sync import sync_to_async
from django.db.models import OuterRef, Subquery, F
from django.apps import apps
from ai_mf_backend.models.v1.database.mf_master_data import *
from ai_mf_backend.models.v1.database.mf_portfolio_nav_dividend import *
from ai_mf_backend.models.v1.database.mf_additional import *
from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable
from ai_mf_backend.models.v1.api.display_high_return_mutual_funds import HighReturnMutualFundsResponse
from ai_mf_backend.utils.v1.api_projection.valid_fields import process_fields
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter

router = APIRouter()


@router.get("/mf_high_return_funds", response_model=HighReturnMutualFundsResponse)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def get_high_return_funds(
    request: Request,
    response: Response,
    page: int = Query(1, gt=0),
    page_size: int = Query(api_config.DEFAULT_PAGE_SIZE, ge=1, le=api_config.MAX_PAGE_SIZE),
):
    try:
        marker_list = ["asset_type", "_1yrret", "total","status"]


        refs = await sync_to_async(lambda: list(MFReferenceTable.objects.filter(marker_name__in=marker_list)))()

        marker_to_models = {
            ref.marker_name: apps.get_model(api_config.PROJECT_NAME,ref.table_name)
            for ref in refs
            if ref.marker_name in marker_list
        }
        # Step 1: Get active scheme codes in a single query
        active_schemecodes = await sync_to_async(
            lambda: set(marker_to_models['status'].objects.filter(
                status="Active"
            ).values_list("schemecode", flat=True))
        )()

        # Step 2: Build a single efficient queryset with all annotations
        base_query = MFSchemeMasterInDetails.objects.filter(schemecode__in=active_schemecodes)

        # Add annotations conditionally
        if "_1yrret" in marker_to_models:
            base_query = base_query.annotate(_1yrret=Subquery(
                marker_to_models["_1yrret"].objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("_1yrret")[:1]
            ))

        if "total" in marker_to_models:
            base_query = base_query.annotate(total=Subquery(
                marker_to_models["total"].objects.filter(
                    schemecode=OuterRef("schemecode")
                ).values("total")[:1]
            ))

        if "asset_type" in marker_to_models:
            base_query = base_query.annotate(asset_type=Subquery(
                marker_to_models["asset_type"].objects.filter(
                    classcode=OuterRef("classcode")
                ).values("asset_type")[:1]
            ))

        
        ordered_query = base_query.order_by(F("_1yrret").desc(nulls_last=True))

        
        result_query = ordered_query.values("schemecode", "total", "_1yrret", "asset_type", "s_name")

    
        full_results = await sync_to_async(lambda: list(result_query))()

        total_count = len(full_results)
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size
        paginated_qs = full_results[offset: offset + page_size]

        return HighReturnMutualFundsResponse(
            status=True,
            message="Success",
            page=page,
            total_pages=total_pages,
            total_data=total_count,
            data=paginated_qs,
            status_code=200,
        )

    except Exception as e:
        response.status_code = 400
        return HighReturnMutualFundsResponse(
            status=False,
            message=f"Error occurred: {str(e)}",
            page=0,
            total_pages=0,
            total_data=0,
            data=[],
            status_code=400,
        )
