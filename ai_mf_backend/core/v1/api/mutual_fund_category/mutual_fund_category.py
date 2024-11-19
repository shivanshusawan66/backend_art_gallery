from fastapi import APIRouter, Response
from ai_mf_backend.models.v1.api.mutual_fund_category import Fund, FrontendResponse
from ai_mf_backend.utils.v1.load_json import load_funds_data

router = APIRouter()


@router.get("/api/mutual_funds_category", response_model=FrontendResponse)
async def get_funds(response: Response):
    """
    API to fetch all funds for the frontend.
    """

    funds_data = load_funds_data()

    funds_list = [Fund(**fund) for fund in funds_data]

    response.status_code = 200

    return FrontendResponse(
        status=True,
        message="Funds fetched successfully.",
        data=funds_list,
        status_code=200,
    )
