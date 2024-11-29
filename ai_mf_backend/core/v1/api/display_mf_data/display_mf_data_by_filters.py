from decimal import Decimal
from typing import Optional
from math import ceil
from fastapi import APIRouter, Query, Request
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.utils.v1.display_mf_data_by_filter.display_mf_data_by_filter import (
    get_mutual_funds_filters_query,
    process_mutual_funds,
)

from ai_mf_backend.models.v1.api.display_mf_data_by_filters import (
    MutualFundFilterResponse,
)
from ai_mf_backend.config.v1.api_config import api_config


router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/mutual-funds/filter", response_model=MutualFundFilterResponse)
async def filter_mutual_funds(
    request: Request,
    fund_family: Optional[str] = Query(None),
    morningstar_rating: Optional[str] = Query(None),
    min_investment: Optional[Decimal] = Query(None),
    Selected_columns: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    try:
        base_query = await get_mutual_funds_filters_query(
            fund_family,
            morningstar_rating,
            min_investment,
        )

        mutual_funds, total_count = await process_mutual_funds(
            base_query, page, page_size
        )

        if total_count == 0:
            return MutualFundFilterResponse(
                status=False,
                message="No mutual funds found matching the specified filter.",
                data=[],
                total_count=0,
                current_page=page,
                total_pages=0,
                status_code=404,
            )

        fixed_columns = [
            "fund_id",
            "scheme_name",
            "morningstar_rating",
            "fund_family",
            "net_asset_value",
            "min_investment",
        ]

        processed_mutual_funds = []

        selected_fields = Selected_columns.split(",") if Selected_columns else []

        for fund in mutual_funds:
            fund_dict = {}

            for field in fixed_columns + selected_fields:
                if hasattr(fund, field):
                    value = getattr(fund, field, None)
                    if value is not None:
                        fund_dict[field] = value

            processed_mutual_funds.append(fund_dict)

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
        return MutualFundFilterResponse(
            status=False,
            message=f"An unexpected error occurred: {str(e)}",
            data=[],
            total_count=0,
            current_page=page,
            total_pages=0,
            status_code=500,
        )
