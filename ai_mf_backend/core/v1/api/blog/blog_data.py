from typing import Optional

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

from ai_mf_backend.utils.v1.api_projection.valid_fields import process_fields, validate_query_params
from ai_mf_backend.utils.v1.validators.blogs import validate_blog_category_id, validate_blog_id

router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/filter_and_select_blog_data",
    response_model=BlogCardResponse,
)
async def filter_and_select_blog_data(
    request: Request,  
    response: Response,
    fields: Optional[str] = Query(
        default=None, description="Comma-separated list of fields to include"
    ),
    blog_id: Optional[int] = Query(
        default=None, description="ID of the blog to filter"
    ),
    category_id: Optional[int] = Query(
        default=None, description="Category to filter the blogs"
    ),
    # Add additional filter parameters here as needed
):
    allowed_params = ["fields", "category_id", "blog_id"]
    try:
        validate_query_params(dict(request.query_params), allowed_params)
    except ValueError as e:
        response.status_code = 400
        return BlogCardResponse(
            status=False,
            message=str(e),
            data=[],
            status_code=response.status_code,
        )
    
    all_fields = api_config.BLOG_DATA_COLUMNS

    try:
        fields_to_project = process_fields(fields, all_fields)
        if "category" in fields_to_project:
            fields_to_project.append("category__name")    
    except ValueError as e:
        response.status_code = 400
        return BlogCardResponse(
            status=False,
            message=str(e),
            data=[],
            status_code=response.status_code,
        )

    filter_kwargs = {}
    try:
        if blog_id is not None:
            blog_id = await validate_blog_id(blog_id)
            filter_kwargs["id"] = blog_id
        if category_id is not None:
            category_id = await validate_blog_category_id(category_id)
            filter_kwargs["category"] = category_id
    except ValidationError as e:
        response.status_code = 400
        return BlogCardResponse(
            status=False,
            message=str(e),
            data=[],
            status_code=400,
        )

    try:
        blogs = await sync_to_async(list)(
        BlogData.objects.filter(deleted=False, **filter_kwargs)
        .values(*fields_to_project)
)

        # Changing name from category__name to category
        for blog in blogs:
            if 'category__name' in blog:
                blog['category'] = blog.pop('category__name')

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