from fastapi import APIRouter, Query, Response, status, Request
from ai_mf_backend.models.v1.api.mf_recommendations import MFRecommendationsResponse
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter

router = APIRouter()

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/mf_recommendations", response_model=MFRecommendationsResponse)
async def get_high_return_funds(
    request: Request,
    response: Response,
    page: int = Query(1, gt=0),
    page_size: int = Query(api_config.DEFAULT_PAGE_SIZE, ge=1, le=api_config.MAX_PAGE_SIZE),
):
    response.status_code = status.HTTP_200_OK
    return MFRecommendationsResponse(
            status=True,
            message="Success",
            page=page,
            total_pages=10,
            total_data=10,
            data=[{
                "schemecode": 44234,
                "s_name": "Nippon India Equity Hybrid Fund-Segregated Portfolio 1-(Q-IDCW)-Direct Plan",
                "nav": 10.345,
                "_1yrret": 126.760563380282,
                "asset_type": "Hybrid"
            },
            {
                "schemecode": 44234,
                "s_name": "Nippon India Equity Hybrid Fund-Segregated Portfolio 1-(Q-IDCW)-Direct Plan",
                "nav": 10.345,
                "_1yrret": 126.760563380282,
                "asset_type": "Hybrid"
            },
            {
                "schemecode": 44228,
                "s_name": "Nippon India Equity Hybrid Fund-Segregated Portfolio 1-(IDCW)",
                "nav": 10.345,
                "_1yrret": 126.415094339623,
                "asset_type": "Hybrid"
            },
            {
                "schemecode": 44228,
                "s_name": "Nippon India Equity Hybrid Fund-Segregated Portfolio 1-(IDCW)",
                "nav": 10.345,
                "_1yrret": 126.415094339623,
                "asset_type": "Hybrid"
            },
            {
                "schemecode": 44229,
                "s_name": "Nippon India Equity Hybrid Fund-Segregated Portfolio 1-(M-IDCW)",
                "nav": 10.345,
                "_1yrret": 126.262626262626,
                "asset_type": "Hybrid"
            }],
            status_code=200,
        )