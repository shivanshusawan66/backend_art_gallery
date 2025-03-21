from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Request, Response, Depends, Query, status
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError

from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.models.v1.database.blog import(
    BlogData,
)
from ai_mf_backend.models.v1.api.blog_data import(
    BlogCardResponse,
)

from ai_mf_backend.utils.v1.processor.processor import (
    process_fields,
)
from ai_mf_backend.utils.v1.validators.blogs import validate_blog_category, validate_blog_id

router = APIRouter()


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
    category: Optional[str] = None,
    blog_id : Optional[int] = None,
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
    
    try:
        if category is not None:
            category = await validate_blog_category(category)
        if blog_id is not None:
            blog_id = await validate_blog_id(blog_id)
    except ValidationError as e:
        response.status_code = 400
        return BlogCardResponse(
            status=False,
            message=str(e),
            data=[],
            status_code=400,
        )

    filter_kwargs = {}
    if category is not None:
        filter_kwargs["category"] = category
    if blog_id is not None:
        filter_kwargs["id"] = blog_id
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