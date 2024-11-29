from fastapi import APIRouter, Request, Response

from ai_mf_backend.core.v1.api import limiter


from ai_mf_backend.utils.v1.constants import FILTER_OPTIONS

from ai_mf_backend.models.v1.api.display_mf_data_filter_option import (
    APIResponse,
    FundFamiliesResponseModel,
)

from ai_mf_backend.config.v1.api_config import api_config

router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/mutual_funds_filter_options/",
    response_model=APIResponse,
)
async def mutual_funds_filter_options(request: Request, response: Response):
    try:
        if FILTER_OPTIONS:
            response.status_code = 200
            return APIResponse(
                status=True,
                message="Filters options fetched successfully",
                data=FundFamiliesResponseModel(
                    fund_family=FILTER_OPTIONS["fund_families"],
                    morningstar_ratings=FILTER_OPTIONS["morningstar_ratings"],
                    min_initial_investment=FILTER_OPTIONS["min_initial_investments"],
                ),
                status_code=200,
            )
        else:
            response.status_code = 404
            return APIResponse(
                status=False,
                message="No data found",
                status_code=404,
            )

    except Exception as e:
        response.status_code = 500
        return APIResponse(
            status=False,
            message="An error occurred while fetching data.",
            status_code=500,
        )
