from math import ceil
from typing import List, Optional

from fastapi import APIRouter, Query, Request, Response

from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.utils.v1.constants import projection_table_object
from ai_mf_backend.utils.v1.database.display_mf_data_by_filter import (
    get_mutual_funds_filters_query,
    process_mutual_funds,
)
from ai_mf_backend.models.v1.database.mutual_fund import MutualFund
from ai_mf_backend.models.v1.api.display_mf_data_by_filters import (
    MutualFundFilterResponse,
)
from ai_mf_backend.config.v1.api_config import api_config

router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/mutual_funds_recommendations/filter", response_model=MutualFundFilterResponse
)
async def filter_mutual_funds(
    response: Response,
    request: Request,
    selected_columns: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(
        api_config.DEFAULT_PAGE_SIZE, ge=1, le=api_config.MAX_PAGE_SIZE
    ),
    k: Optional[int] = Query(None, ge=1),
):
    try:
        selected_fields = (
            [col.strip() for col in selected_columns.split(",")]
            if selected_columns
            else []
        )

        if not len(selected_fields):
            selected_fields = api_config.DEFAULT_ALL_MF_DISPLAY_COLUMNS

        projections_diff = set(selected_fields) - set(
            projection_table_object.valid_projections
        )

        if len(projections_diff):
            response.status_code = 404
            return MutualFundFilterResponse(
                status=False,
                message=f"The following projections are not recognized -> {projections_diff}",
                data=[],
                total_count=0,
                current_page=page,
                total_pages=0,
                status_code=404,
            )

        select_related_models: List[str] = []

        for projection in selected_fields:
            projection_mapping = projection_table_object.mapping[projection]
            select_related_models.append(
                f"{projection_mapping['table_name']}__{projection_mapping['column_name']}"
            )

        base_query = MutualFund.objects.select_related(
            *select_related_models
        ).prefetch_related("trailing_returns", "annual_returns", "risk_statistics")

        selected_fields_for_query = selected_fields
        base_query = base_query.only(*selected_fields_for_query)

        base_query = await get_mutual_funds_filters_query()

        if k is not None and k > 0:
            base_query = base_query[:k]

        mutual_funds, total_count = await process_mutual_funds(
            base_query, page, page_size
        )

        if total_count == 0:
            response.status_code = 404
            return MutualFundFilterResponse(
                status=False,
                message="No mutual funds found matching the specified filter.",
                data=[],
                total_count=0,
                current_page=page,
                total_pages=0,
                status_code=404,
            )

        processed_mutual_funds = [
            {
                **{
                    field: getattr(fund, field, None)
                    for field in api_config.DEFAULT_ALL_MF_DISPLAY_COLUMNS
                },
                **{field: getattr(fund, field, None) for field in selected_fields},
            }
            for fund in mutual_funds
        ]

        if k is not None:
            processed_mutual_funds = processed_mutual_funds[:k]

        response.status_code = 200
        return MutualFundFilterResponse(
            status=True,
            message="Successfully fetched mutual funds based on the applied filters.",
            data=processed_mutual_funds,
            total_count=min(total_count, k) if k else total_count,
            current_page=page,
            total_pages=(
                ceil(min(total_count, k) / page_size)
                if k
                else ceil(total_count / page_size)
            ),
            status_code=200,
        )

    except Exception as e:
        response.status_code = 500
        return MutualFundFilterResponse(
            status=False,
            message="An unexpected error occurred: {error}".format(error=str(e)),
            data=[],
            total_count=0,
            current_page=page,
            total_pages=0,
            status_code=500,
        )
