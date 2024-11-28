from fastapi import APIRouter, Query, Request
from fastapi import HTTPException
from decimal import Decimal
from typing import Optional
from django.db.models import Q
from asgiref.sync import sync_to_async
from pydantic import ValidationError
from ai_mf_backend.models.v1.database.mutual_fund import MutualFund
from ai_mf_backend.models.v1.api.display_mf_data_by_filters import (
    MutualFundFilterResponse,
    MutualFundModel,
    ErrorResponse,
)
from ai_mf_backend.utils.v1.Pagination import paginate_queryset
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter
from math import ceil

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

        query = await sync_to_async(
            lambda: MutualFund.objects.select_related(
                "overview", "performance_data", "fund_data"
            ).prefetch_related("trailing_returns", "annual_returns", "risk_statistics")
        )()

        filters = Q()

        if fund_family and fund_family.lower() != "string":
            filters &= Q(overview__fund_family__iexact=fund_family)

        if morningstar_rating and morningstar_rating.lower() != "string":
            try:
                star_count = (
                    morningstar_rating.count("*")
                    if "*" in morningstar_rating
                    else int(morningstar_rating.strip())
                )
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

        base_query = query.filter(filters) if filters else query

        paginated_funds, total_count = await sync_to_async(paginate_queryset)(
            base_query, page=page, page_size=page_size
        )

        if total_count == 0:
            return MutualFundFilterResponse(
                status=False,
                message="No mutual funds found matching the specified filter.",
                data=[],
                total_count=total_count,
                current_page=page,
                total_pages=ceil(total_count / page_size),
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
                category=fund.overview.category if fund.overview else None,
                net_assets=fund.overview.net_assets if fund.overview else None,
                yield_value=fund.overview.yield_value if fund.overview else None,
                inception_date=fund.overview.inception_date if fund.overview else None,
                min_investment=(
                    fund.fund_data.min_initial_investment
                    if fund.fund_data
                    else Decimal("0")
                ),
                min_subsequent_investment=(
                    fund.fund_data.min_subsequent_investment
                    if fund.fund_data
                    else Decimal("0")
                ),
                performance_ytd_return=(
                    fund.performance_data.ytd_return if fund.performance_data else None
                ),
                performance_average_return_5y=(
                    fund.performance_data.average_return_5y
                    if fund.performance_data
                    else None
                ),
                morningstar_return_rating=(
                    fund.performance_data.morningstar_return_rating
                    if fund.performance_data
                    else None
                ),
                number_of_years_up=(
                    fund.performance_data.number_of_years_up
                    if fund.performance_data
                    else 0
                ),
                number_of_years_down=(
                    fund.performance_data.number_of_years_down
                    if fund.performance_data
                    else 0
                ),
                best_3y_total_return=(
                    fund.performance_data.best_3y_total_return
                    if fund.performance_data
                    else Decimal(0.00)
                ),
                worst_3y_total_return=(
                    fund.performance_data.worst_3y_total_return
                    if fund.performance_data
                    else Decimal(0.00)
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
