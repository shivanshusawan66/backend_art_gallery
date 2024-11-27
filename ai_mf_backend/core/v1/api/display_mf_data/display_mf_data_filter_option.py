from asgiref.sync import sync_to_async
from ai_mf_backend.core.v1.api import limiter
from fastapi import APIRouter, Request, Response
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.models.v1.database.mutual_fund import FundOverview, FundData
from ai_mf_backend.models.v1.api.display_mf_data_filter_option import (
    FundFamiliesResponseModel,
    ErrorResponse,
    SuccessResponse,
)

router = APIRouter()

MORNINGSTAR_RATING_MAP = {"*": 1, "**": 2, "***": 3, "****": 4, "*****": 5, "": 0}


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/mutual_funds_filter_options/",
    response_model=SuccessResponse,
)
async def get_fund_families(request: Request, response: Response):

    try:
        fund_families = await sync_to_async(list)(
            FundOverview.objects.values_list("fund_family", flat=True).distinct()
        )
        morningstar_ratings = await sync_to_async(list)(
            FundOverview.objects.values_list("morningstar_rating", flat=True).distinct()
        )
        min_initial_investments = await sync_to_async(list)(
            FundData.objects.values_list("min_initial_investment", flat=True).distinct()
        )

        fund_families_sorted = sorted(fund_families)
        morningstar_ratings_numeric = sorted(
            [MORNINGSTAR_RATING_MAP.get(rating, 0) for rating in morningstar_ratings]
        )
        min_initial_investments_sorted = sorted(
            float(i) for i in min_initial_investments
        )

        if (
            fund_families_sorted
            or morningstar_ratings_numeric
            or min_initial_investments_sorted
        ):
            response.status_code = 200
            return SuccessResponse(
                status=True,
                message="Filters options fetched successfully",
                data=FundFamiliesResponseModel(
                    fund_family=fund_families_sorted,
                    morningstar_ratings=morningstar_ratings_numeric,
                    min_initial_investment=min_initial_investments_sorted,
                ),
                status_code=200,
            )
        else:
            response.status_code = 404
            return ErrorResponse(
                status=False,
                message="No data found",
                error_details=None,
                status_code=404,
            )

    except Exception as e:
        response.status_code = 500
        return ErrorResponse(
            status=False,
            message="An error occurred while fetching data.",
            error_details=str(e),
            status_code=500,
        )
