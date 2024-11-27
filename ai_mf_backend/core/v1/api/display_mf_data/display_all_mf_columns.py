from asgiref.sync import sync_to_async
from ai_mf_backend.core.v1.api import limiter
from fastapi import APIRouter, Request, Response
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.models.v1.database.mutual_fund import Reference
from ai_mf_backend.models.v1.api.display_all_mf_columns import (
    ErrorResponse,
    SuccessResponse,
)

router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/mutual_funds_all_columns/",
    response_model=SuccessResponse,
    responses={200: {"model": SuccessResponse}, 404: {"model": ErrorResponse}},
)
async def mutual_funds_all_columns(request: Request, response: Response):
    try:
        column_names = await sync_to_async(list)(
            Reference.objects.values_list("column_name", flat=True)
        )

        if column_names:
            response.status_code = 200
            return SuccessResponse(
                status=True,
                message="Successfully retrieved references columns",
                columns=column_names,
                status_code=200,
            )
        else:
            response.status_code = 404
            return ErrorResponse(
                status=False, message="No  mutualfunds columns  found", status_code=404
            )

    except Exception as e:
        response.status_code = 500
        return ErrorResponse(
            status=False,
            message="Failed to retrieve mutualfunds columns",
            status_code=500,
        )
