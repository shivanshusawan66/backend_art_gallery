from typing import Optional
from datetime import datetime

from django.forms import ValidationError
from fastapi import APIRouter, HTTPException, Request, Response, Depends, Query, status
from asgiref.sync import sync_to_async

from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.models.v1.database.blog import(
    BlogData,
)
from ai_mf_backend.models.v1.api.blog_data import(
    BlogCardResponse,
)

from ai_mf_backend.utils.v1.display_fund_data.display_each import (
    process_fields,
)
from ai_mf_backend.utils.v1.validators.blogs import validate_blog_category

router = APIRouter()


# @router.get(
#     "/blog_data",
#     status_code=status.HTTP_200_OK,
#     response_model=BlogCardResponse,
# )
# async def blog_data(
#     response: Response,
#     fields: Optional[str] = Query(
#         default=None, description="Comma-separated list of fields to include"
#     ),
# ):
#     all_fields = api_config.BLOG_DATA_COLUMNS

#     try:
#         fields_to_project = process_fields(fields, all_fields)
#     except ValueError as e:
#         response.status_code = 400
#         return BlogCardResponse(
#             status=False,
#             message=str(e),
#             data=[],
#             status_code=response.status_code,
#         )

#     try:
#         blogs = await sync_to_async(list)(
#             BlogData.objects.all().values(*fields_to_project)
#         )

#         if blogs:
#             response.status_code = 200
#             return BlogCardResponse(
#                 status=True,
#                 message="Successfully retrieved blog data",
#                 data=blogs,
#                 status_code=response.status_code,
#             )
#         else:
#             response.status_code = 404
#             return BlogCardResponse(
#                 status=False,
#                 message="No blog data found",
#                 data=[],
#                 status_code=response.status_code,
#             )
#     except Exception as e:
#         response.status_code = 500
#         return BlogCardResponse(
#             status=False,
#             message=f"Error retrieving blog cards: {str(e)}",
#             data=[],
#             status_code=response.status_code,
#         )


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/filter_and_select_blog_data",
    status_code=status.HTTP_200_OK,
    response_model=BlogCardResponse,
)
async def filter_and_select_blog_data(
    request: Request,  
    response: Response,
    fields: Optional[str] = Query(
        default=None, description="Comma-separated list of fields to include"
    ),
    category: Optional[str] = Depends(validate_blog_category),
    # Add additional filter parameters here as needed
):
    all_fields = api_config.BLOG_DATA_COLUMNS

    try:
        fields_to_project = process_fields(fields, all_fields)
    except ValueError as e:
        response.status_code = 400
        return BlogCardResponse(
            status=False,
            message=str(e),
            data=[],
            status_code=response.status_code,
        )

    filter_kwargs = {}
    if category is not None:
        filter_kwargs["category"] = category
    # Add additional filters to the dictionary here

    try:
        blogs = await sync_to_async(list)(
            BlogData.objects.filter(**filter_kwargs).values(*fields_to_project)
        )

        if blogs:
            response.status_code = 200
            return BlogCardResponse(
                status=True,
                message="Successfully retrieved blog data",
                data=blogs,
                status_code=response.status_code,
            )
        else:
            response.status_code = 404
            return BlogCardResponse(
                status=False,
                message="No blog data found matching the criteria",
                data=[],
                status_code=response.status_code,
            )
    except Exception as e:
        response.status_code = 500
        return BlogCardResponse(
            status=False,
            message=f"Error retrieving blog cards: {str(e)}",
            data=[],
            status_code=response.status_code,
        )