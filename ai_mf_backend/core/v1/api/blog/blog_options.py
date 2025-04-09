from fastapi import APIRouter
from ai_mf_backend.models.v1.api.blog_data import BlogCategoryOptionResponse
from ai_mf_backend.models.v1.database.blog import BlogCategory

from asgiref.sync import sync_to_async

router = APIRouter()


@router.get("/options_blog_category", response_model=BlogCategoryOptionResponse)
async def get_blog_category_options():
    try:
        categories = await sync_to_async(list)(BlogCategory.objects.all())

        category_options = [
            {
                "key": int(category.id),
                "label": category.name,
                "value": category.name.lower(),
            }
            for category in categories
        ]

        data = {
            "blog_categories": {
                "name": "blog_category",
                "label": "Blog Category",
                "options": category_options,
                "type": "dropdown",
                "default": [category_options[0]["key"]] if category_options else [],
                "required": False,
            }
        }

        return BlogCategoryOptionResponse(
            status=True,
            message="Blog category options fetched successfully",
            data=data,
            status_code=200,
        )

    except Exception as e:
        return BlogCategoryOptionResponse(
            status=False,
            message=f"Failed to fetch blog category options: {str(e)}",
            data={},
            status_code=500,
        )
