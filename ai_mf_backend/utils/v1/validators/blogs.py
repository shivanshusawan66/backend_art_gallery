from typing import Optional
from asgiref.sync import sync_to_async
from fastapi import HTTPException

from ai_mf_backend.models.v1.database.blog import BlogCategory

async def validate_blog_category(value: Optional[str] = None):
    """
    Validator to ensure a category exists in BlogCategory.
    """
    if value:
        exists = await sync_to_async(BlogCategory.objects.filter(name=value).exists)()
        if not exists:
            raise HTTPException(status_code=400, detail=f"Invalid category: {value}")
    return value