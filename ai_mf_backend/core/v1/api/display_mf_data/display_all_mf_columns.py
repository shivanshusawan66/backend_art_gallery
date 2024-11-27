from asgiref.sync import sync_to_async
from fastapi import APIRouter, Request, Response
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.models.v1.database.mutual_fund import Reference
from ai_mf_backend.models.v1.api.display_all_mf_columns import (
    ColumnModel,
    ErrorResponse,
    SuccessResponse,
)

router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/references/",
    response_model=SuccessResponse,
    responses={200: {"model": SuccessResponse}, 404: {"model": ErrorResponse}},
)
async def get_references_column(request: Request, response: Response):
    try:
        column_names = await sync_to_async(list)(
            Reference.objects.values_list("column_name", flat=True)
        )

        if column_names:
            columns = [ColumnModel(column_name=name) for name in column_names]

            success_response = SuccessResponse(
                status=True,
                status_code=200,
                message="Successfully retrieved references columns",
                columns=columns,
            )
            response.status_code = 200
            return success_response

        error_response = ErrorResponse(
            status=False,
            status_code=404,
            message="No references found",
            error_details="The references columns is empty",
        )
        response.status_code = 404
        return error_response

    except Exception as e:
        error_response = ErrorResponse(
            status=False,
            status_code=500,
            message="Failed to retrieve references columns",
            error_details=str(e),
        )
        response.status_code = 500
        return error_response
