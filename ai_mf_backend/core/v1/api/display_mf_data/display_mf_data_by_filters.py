from math import ceil
from decimal import Decimal
from fastapi import Request
from typing import Optional
from django.db.models import Q
from pydantic import ValidationError
from fastapi import APIRouter, Query, Request
from asgiref.sync import sync_to_async
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.utils.v1.Pagination import paginate_queryset
from ai_mf_backend.models.v1.database.mutual_fund import MutualFund

from ai_mf_backend.models.v1.api.display_mf_data_by_filters import (
    MutualFundFilterResponse,
    MutualFundModel,
    ErrorResponse,
)

router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/mutual-funds/filter", response_model=MutualFundFilterResponse)
async def filter_mutual_funds(
    request: Request,
    fund_family: Optional[str] = Query(None),
    morningstar_rating: Optional[str] = Query(None),
    min_investment_range_start: Optional[Decimal] = Query(None),
    min_investment_range_end: Optional[Decimal] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    try:

        @sync_to_async
        def get_query():
            return MutualFund.objects.select_related("overview", "fund_data").only(
                "scheme_name",
                "net_asset_value",
                "overview__morningstar_rating",
                "overview__fund_family",
                "fund_data__min_initial_investment",
                "overview__ytd_return",
            )

        query = await get_query()

        filters = Q()
        if fund_family and fund_family.lower() != "string":
            filters &= Q(overview__fund_family__iexact=fund_family)
        if morningstar_rating and morningstar_rating.lower() != "string":
            try:
                if "*" in morningstar_rating:
                    star_count = morningstar_rating.count("*")
                else:
                    star_count = int(morningstar_rating.strip())
                if 1 <= star_count <= 5:
                    star_filter = "*" * star_count
                    filters &= Q(overview__morningstar_rating__exact=star_filter)
            except ValueError:
                return ErrorResponse(
                    status=False,
                    message="Invalid Morningstar Rating format",
                    status_code=400,
                )
        if min_investment_range_start and min_investment_range_start > Decimal("0"):
            filters &= Q(
                fund_data__min_initial_investment__gte=min_investment_range_start
            )

        if min_investment_range_end and min_investment_range_end > Decimal("0"):
            filters &= Q(
                fund_data__min_initial_investment__lte=min_investment_range_end
            )

        base_query = query.filter(filters) if filters != Q() else query

        # Use sync_to_async for pagination
        @sync_to_async
        def paginate(queryset, page, page_size):
            return paginate_queryset(queryset, page=page, page_size=page_size)

        paginated_funds, total_count = await paginate(base_query, page, page_size)

        if total_count == 0:
            return MutualFundFilterResponse(
                status=False,
                message="No mutual funds found matching the specified filter.",
                data=[],
                status_code=404,
            )
        mutual_funds = [
            MutualFundModel(
                scheme_name=fund.scheme_name,
                net_asset_value=fund.net_asset_value,
                ytd_return=fund.overview.ytd_return if fund.overview else None,
                morningstar_rating=(
                    fund.overview.morningstar_rating if fund.overview else None
                ),
                fund_family=fund.overview.fund_family if fund.overview else None,
                min_investment=(
                    fund.fund_data.min_initial_investment
                    if fund.fund_data
                    else Decimal("0")
                ),
            )
            for fund in paginated_funds
        ]
        return MutualFundFilterResponse(
            status=True,
            message="Successfully fetched mutual funds based on the applied filters.",
            data=mutual_funds,
            total_count=total_count,
            current_page=page,
            total_pages=ceil(total_count / page_size),
            status_code=200,
        )

    except ValidationError as ve:
        return ErrorResponse(
            status=False, message=f"Validation error: {str(ve)}", status_code=422
        )

    except Exception as e:
        return ErrorResponse(
            status=False,
            message=f"An unexpected error occurred: {str(e)}",
            status_code=500,
        )
