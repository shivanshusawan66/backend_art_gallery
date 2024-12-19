from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter
from fastapi import APIRouter, HTTPException, Response, Request

from ai_mf_backend.models.v1.api.mutual_fund_category import (
    ErrorResponse,
    FundCategory,
    FrontendResponse,
)

router = APIRouter()

fund_categories = fund_categories = [
    {
        "id": 1,
        "image": "https://static.smartspends.com/static/images/etmoneyweb/category-icons/large-cap.svg",
        "name": "Large Cap",
        "desc": "Invest in Top 100 Stocks",
    },
    {
        "id": 2,
        "image": "https://static.smartspends.com/static/images/etmoneyweb/category-icons/mid-cap.svg",
        "name": "Mid Cap",
        "desc": "Invest in Top 150 Stocks",
    },
    {
        "id": 3,
        "image": "https://static.smartspends.com/static/images/etmoneyweb/category-icons/small-cap.svg",
        "name": "Small Cap",
        "desc": "Invest in Top 100 Stocks",
    },
    {
        "id": 4,
        "image": "https://static.smartspends.com/static/images/etmoneyweb/category-icons/large-and-midcap.svg",
        "name": "Mid and Large Cap",
        "desc": "Passively Invest in Top 100 companies",
    },
]


router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/mutual_funds_category",
    response_model=FrontendResponse,
    status_code=200,
)
async def get_funds(request: Request, response: Response):
    """
    API to fetch all mutual fund categories for the frontend, with rate limiting and login required.
    """
    try:
        if not fund_categories:
            raise HTTPException(status_code=400, detail="No fund categories available")

        categories_list = [FundCategory(**category) for category in fund_categories]

        response.status_code = 200

        return FrontendResponse(
            status=True,
            message="Fund categories fetched successfully.",
            data=categories_list,
            status_code=200,
        )

    except HTTPException as e:
        response.status_code = e.status_code
        return ErrorResponse(
            status=False,
            message=e.detail,
            data=None,
            status_code=e.status_code,
        )
    except Exception as e:
        response.status_code = 500
        return ErrorResponse(
            status=False,
            message="Internal Server Error: " + str(e),
            data=None,
            status_code=500,
        )
