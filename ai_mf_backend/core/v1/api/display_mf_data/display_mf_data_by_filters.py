from math import ceil
from typing import List, Optional

from fastapi import APIRouter, Query, Request, Response

from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.utils.v1.constants import (
    COLUMN_MAPPING,
    ERROR_MESSAGES,
)
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
@router.get("/mutual-funds/filter", response_model=MutualFundFilterResponse)
async def filter_mutual_funds(
    response: Response,
    request: Request,
    fund_family: Optional[str] = Query(None),
    morningstar_rating: Optional[str] = Query(None),
    min_investment: Optional[float] = Query(None),
    selected_columns: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(
        api_config.DEFAULT_PAGE_SIZE, ge=1, le=api_config.MAX_PAGE_SIZE
    ),
):
    try:
        selected_fields = (
            [col.strip() for col in selected_columns.split(",")]
            if selected_columns
            else []
        )

        if not len(selected_fields):
            selected_fields = api_config.DEFAULT_DISPLAY_COLUMNS

        select_related_models: List[str] = []

        for col in selected_fields + api_config.DEFAULT_DISPLAY_COLUMNS:
            if col in COLUMN_MAPPING:
                related_model = COLUMN_MAPPING[col][1]
                if related_model and related_model not in select_related_models:
                    select_related_models.append(related_model)

        base_query = MutualFund.objects.select_related(
            *select_related_models
        ).prefetch_related("trailing_returns", "annual_returns", "risk_statistics")

        selected_fields_for_query = api_config.DEFAULT_DISPLAY_COLUMNS + selected_fields
        base_query = base_query.only(*selected_fields_for_query)

        base_query = await get_mutual_funds_filters_query(
            fund_family, morningstar_rating, min_investment
        )

        mutual_funds, total_count = await process_mutual_funds(
            base_query, page, page_size
        )

        if total_count == 0:
            response.status_code = 404
            return MutualFundFilterResponse(
                status=False,
                message=ERROR_MESSAGES["no_mutual_funds_found"],
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
                    for field in api_config.DEFAULT_DISPLAY_COLUMNS
                },
                **{field: getattr(fund, field, None) for field in selected_fields},
            }
            for fund in mutual_funds
        ]

        response.status_code = 200
        return MutualFundFilterResponse(
            status=True,
            message="Successfully fetched mutual funds based on the applied filters.",
            data=processed_mutual_funds,
            total_count=total_count,
            current_page=page,
            total_pages=ceil(total_count / page_size),
            status_code=200,
        )

    except Exception as e:
        response.status_code = 500
        return MutualFundFilterResponse(
            status=False,
            message=ERROR_MESSAGES["unexpected_error"].format(error=str(e)),
            data=[],
            total_count=0,
            current_page=page,
            total_pages=0,
            status_code=500,
        )
