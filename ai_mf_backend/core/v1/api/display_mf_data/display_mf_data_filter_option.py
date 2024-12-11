import logging

from fastapi import APIRouter, Request, Response

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.utils.v1.constants import MFFilterOptions, filter_option_object

from ai_mf_backend.models.v1.api.display_mf_data_filter_option import (
    APIResponse,
    FundFamiliesResponseModel,
)

from ai_mf_backend.config.v1.api_config import api_config


logger = logging.getLogger(__name__)
router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/mutual_funds_filter_options",
    response_model=APIResponse,
)
async def mutual_funds_filter_options(request: Request, response: Response):
    try:
        fund_families = filter_option_object.fund_families
        morningstar_ratings = filter_option_object.morningstar_rating
        min_initial_investments = filter_option_object.min_initial_investments

        if not all(
            [
                fund_families,
                morningstar_ratings,
                min_initial_investments,
            ]
        ):
            response.status_code = 404
            return APIResponse(
                status=False,
                message="No data found",
                data=dict(),
                status_code=404,
            )
        response.status_code = 200
        return APIResponse(
            status=True,
            message="Filters options fetched successfully",
            data=FundFamiliesResponseModel(
                fund_family=fund_families,
                morningstar_ratings=morningstar_ratings,
                min_initial_investment=min_initial_investments,
                categories=[
                    {"id": key, "name": value}
                    for key, value in MFFilterOptions.CATEGORY_MAPPING.items()
                ],
            ),
            status_code=200,
        )

    except Exception as e:
        response.status_code = 500
        return APIResponse(
            status=False,
            message="An error occurred while fetching data.",
            status_code=500,
        )
