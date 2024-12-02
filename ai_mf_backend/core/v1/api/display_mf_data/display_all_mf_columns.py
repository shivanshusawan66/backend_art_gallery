from asgiref.sync import sync_to_async
from fastapi import APIRouter, Request, Response
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.models.v1.api.display_all_mf_columns import ResponseModel
from ai_mf_backend.models.v1.database.mutual_fund import Reference
from ai_mf_backend.config.v1.api_config import api_config

router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/mutual_funds_all_columns/",
    response_model=ResponseModel,
    responses={200: {"model": ResponseModel}, 404: {"model": ResponseModel}},
)
async def mutual_funds_all_columns(request: Request, response: Response):
    try:
        column_names = await sync_to_async(list)(
            Reference.objects.only("column_name").values_list("column_name", flat=True)
        )

        if column_names:
            response.status_code = 200
            return ResponseModel(
                status=True,
                message="Successfully retrieved references columns",
                columns=column_names,
                status_code=200,
            )
        else:
            response.status_code = 404
            return ResponseModel(
                status=False,
                message="No mutual funds columns found",
                status_code=404,
            )

    except Exception as e:
        response.status_code = 500
        return ResponseModel(
            status=False,
            message="Failed to retrieve mutual funds columns",
            status_code=500,
        )
