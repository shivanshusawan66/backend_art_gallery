import logging
from decimal import Decimal
from typing import Optional, Any

from asgiref.sync import sync_to_async

from django.db.models import Q

from ai_mf_backend.utils.v1.constants import MFFilterOptions
from ai_mf_backend.utils.v1.pagination import paginate_queryset

from ai_mf_backend.models.v1.database.mutual_fund import MutualFund
from ai_mf_backend.models.v1.api.display_mf_data_by_filters import (
    AnnualReturnModel,
    MutualFundModel,
    TrailingReturnModel,
)

logger = logging.getLogger(__name__)


def process_input_list(input_param, convert_func=str.strip, filter_condition=None):

    if not input_param:
        return []

    if not isinstance(input_param, str):
        return (
            [convert_func(input_param)]
            if filter_condition is None or filter_condition(input_param)
            else []
        )

    processed_list = [
        converted_item
        for item in input_param.split(",")
        if (converted_item := convert_func(item))
        and (filter_condition is None or filter_condition(converted_item))
    ]

    return processed_list


@sync_to_async
def get_mutual_funds_filters_query(
    fund_family: Optional[str] = None,
    morningstar_rating: Optional[str] = None,
    min_investment: Optional[Decimal] = None,
    category: Optional[str] = None,
) -> Any:
    query = MutualFund.objects.select_related(
        "overview", "performance_data", "fund_data"
    ).prefetch_related("trailing_returns", "annual_returns", "risk_statistics")

    filters = Q()

    if fund_family and any(ff.lower() != "string" for ff in fund_family):
        family_filters = Q()
        for family in fund_family:
            if family.lower() != "string":
                family_filters |= Q(overview__fund_family__iexact=family)
        filters &= family_filters

    # Morningstar Rating Filter
    if morningstar_rating and any(mr.lower() != "string" for mr in morningstar_rating):
        rating_filters = Q()
        for rating in morningstar_rating:
            try:
                star_count = rating.count("*") if "*" in rating else int(rating.strip())
                if 1 <= star_count <= 5:
                    rating_filters |= Q(overview__morningstar_rating="*" * star_count)
            except ValueError:
                pass
        if rating_filters:
            filters &= rating_filters

    # Minimum Investment Filter
    if min_investment and any(mi is not None and mi > 0 for mi in min_investment):
        investment_filters = Q()
        for investment in min_investment:
            if investment is not None and investment > 0:
                investment_filters |= Q(fund_data__min_initial_investment=investment)
        filters &= investment_filters

    # Category Filter
    if category:
        category_filters = Q()
        for cat in category:
            category_value = MFFilterOptions.CATEGORY_MAPPING.get(cat)
            if category_value:
                if category_value == "Mid and Large Cap":
                    category_filters |= Q(overview__category="Mid Cap") | Q(
                        overview__category="Large Cap"
                    )
                else:
                    category_filters |= Q(overview__category__iexact=category_value)
        if category_filters:
            filters &= category_filters

    return query.filter(filters) if filters else query


@sync_to_async
def get_paginated_mutual_funds(base_query, page: int, page_size: int):
    return paginate_queryset(base_query, page=page, page_size=page_size)


@sync_to_async
def get_risk_statistic(fund):
    return fund.risk_statistics.first() if fund.risk_statistics.exists() else None


async def process_mutual_funds(base_query, page: int, page_size: int) -> Any:
    paginated_funds, total_count = await get_paginated_mutual_funds(
        base_query, page, page_size
    )

    mutual_funds = []

    for fund in paginated_funds:
        try:
            overview = fund.overview if hasattr(fund, "overview") else None
            performance_data = (
                fund.performance_data if hasattr(fund, "performance_data") else None
            )
            fund_data = fund.fund_data if hasattr(fund, "fund_data") else None

            risk_statistic = await get_risk_statistic(fund)

            trailing_returns = [
                TrailingReturnModel(
                    metric=tr.metric,
                    fund_return=tr.fund_return,
                    benchmark_return=tr.benchmark_return,
                )
                for tr in fund.trailing_returns.all()
            ]

            annual_returns = [
                AnnualReturnModel(
                    year=ar.year,
                    fund_return=ar.fund_return,
                    category_return=ar.category_return,
                )
                for ar in fund.annual_returns.all()
            ]

            # Provide default values for all fields
            mutual_funds.append(
                MutualFundModel(
                    fund_id=fund.id,
                    scheme_name=fund.scheme_name,
                    net_asset_value=fund.net_asset_value,
                    ytd_return=overview.ytd_return if overview else None,
                    morningstar_rating=(
                        overview.morningstar_rating if overview else None
                    ),
                    category=overview.category if overview else None,
                    fund_family=overview.fund_family if overview else None,
                    net_assets=overview.net_assets if overview else None,
                    yield_value=overview.yield_value if overview else None,
                    inception_date=overview.inception_date if overview else None,
                    min_investment=(
                        fund_data.min_initial_investment if fund_data else Decimal("0")
                    ),
                    performance_ytd_return=(
                        performance_data.ytd_return if performance_data else None
                    ),
                    performance_average_return_5y=(
                        performance_data.average_return_5y if performance_data else None
                    ),
                    number_of_years_up=(
                        performance_data.number_of_years_up if performance_data else 0
                    ),
                    number_of_years_down=(
                        performance_data.number_of_years_down if performance_data else 0
                    ),
                    best_3y_total_return=(
                        performance_data.best_3y_total_return
                        if performance_data
                        else Decimal(0.00)
                    ),
                    worst_3y_total_return=(
                        performance_data.worst_3y_total_return
                        if performance_data
                        else Decimal(0.00)
                    ),
                    alpha=risk_statistic.alpha if risk_statistic else Decimal(0.00),
                    beta=risk_statistic.beta if risk_statistic else Decimal(0.00),
                    mean_annual_return=(
                        risk_statistic.mean_annual_return
                        if risk_statistic
                        else Decimal(0.00)
                    ),
                    r_squared=(
                        risk_statistic.r_squared if risk_statistic else Decimal(0.00)
                    ),
                    standard_deviation=(
                        risk_statistic.standard_deviation
                        if risk_statistic
                        else Decimal(0.00)
                    ),
                    sharpe_ratio=(
                        risk_statistic.sharpe_ratio if risk_statistic else Decimal(0.00)
                    ),
                    treynor_ratio=(
                        risk_statistic.treynor_ratio
                        if risk_statistic
                        else Decimal(0.00)
                    ),
                    trailing_returns=trailing_returns,
                    annual_returns=annual_returns,
                )
            )
        except Exception as e:
            # Log the error for the specific fund
            logger.info(f"Error processing fund {fund.id}: {str(e)}")
            # Optionally, you can choose to skip this fund or handle it differently
            continue

    return mutual_funds, total_count
