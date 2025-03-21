from typing import Optional
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError

from ai_mf_backend.models.v1.database.blog import BlogCategory, BlogData

async def validate_blog_category(category: Optional[str] = None):
    """
    Validator to ensure a category exists in BlogCategory.
    """
    if category:
        exists = await sync_to_async(BlogCategory.objects.filter(name=category).exists)()
        if not exists:
            raise ValidationError("Invalid category")
    return category

async def validate_blog_id(blog_id: Optional[int] = None):
    """
    Validator to ensure a blog with the given ID exists in BlogData.
    """  
    if blog_id:
        exists = await sync_to_async(BlogData.objects.filter(id=blog_id).exists)()
        if not exists:
            raise ValidationError("Invalid blog id")
    return blog_id
