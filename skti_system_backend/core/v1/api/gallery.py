from fastapi import APIRouter, Request, Response
from asgiref.sync import sync_to_async

from skti_system_backend.models.v1.api.gallery import(
    ArtworksResponse,
    CategoriesResponse
)
from skti_system_backend.models.v1.database.gallery import (
    Artwork,
    Category
)

router = APIRouter(tags=["Artworks"])

@router.get(
    "/get_all_categories",
    response_model=CategoriesResponse
)
async def get_all_categories(
    request: Request,
    response: Response
):
    """
    Get all categories.
    """

    categories = await sync_to_async(list)(
        Category.objects.all()
    )
    
    if not categories:
        response.status_code = 404
        return {
            "status": False,
            "message": "No categories found",
            "data": [],
            "status_code": 404
        }

    categories_list = [
        {
            "id": category.id,
            "name": category.name,
            "created_at": category.created_at.isoformat(),
            "updated_at": category.updated_at.isoformat()
        } for category in categories
    ]
    
    return CategoriesResponse(
        status=True,
        message="Categories retrieved successfully",
        data=categories_list,
        status_code=200
    )

@router.get(
    "/get_all_artworks",
    response_model=ArtworksResponse
)
async def get_all_artworks(
    request: Request,
    response: Response
):
    """
    Get all artworks.
    """

    artworks = await sync_to_async(list)(
        Artwork.objects.select_related('category').prefetch_related('tags').filter(is_deleted=False)
    )
    
    if not artworks:
        response.status_code = 404
        return {
            "status": False,
            "message": "No artworks found",
            "data": [],
            "status_code": 404
        }

    artworks_list = [
        {
            "id": artwork.id,
            "title": artwork.title,
            "description": artwork.description,
            "category": artwork.category.name if artwork.category else None,
            "image_url": artwork.image.url if artwork.image else None,
            "tags": [tag.name for tag in artwork.tags.all()],
            "is_deleted": artwork.is_deleted,
            "created_at": artwork.created_at.isoformat(),
            "updated_at": artwork.updated_at.isoformat()
        } for artwork in artworks
    ]
    
    return ArtworksResponse(
        status=True,
        message="Artworks retrieved successfully",
        data=artworks_list,
        status_code=200
    )

@router.get(
    "/get_artworks_by_category/{category_id}",
    response_model=ArtworksResponse
)
async def get_artworks_by_category(
    category_id: int,
    request: Request,
    response: Response
):
    """
    Get all artworks for a particular category.
    """

    artworks = await sync_to_async(list)(
        Artwork.objects.select_related('category').prefetch_related('tags').filter(
            is_deleted=False, 
            category_id=category_id
        )
    )
    
    if not artworks:
        response.status_code = 404
        return {
            "status": False,
            "message": f"No artworks found for category ID {category_id}",
            "data": [],
            "status_code": 404
        }

    artworks_list = [
        {
            "id": artwork.id,
            "title": artwork.title,
            "description": artwork.description,
            "category": artwork.category.name if artwork.category else None,
            "image_url": artwork.image.url if artwork.image else None,
            "tags": [tag.name for tag in artwork.tags.all()],
            "is_deleted": artwork.is_deleted,
            "created_at": artwork.created_at.isoformat(),
            "updated_at": artwork.updated_at.isoformat()
        } for artwork in artworks
    ]
    
    return ArtworksResponse(
        status=True,
        message=f"Artworks for category ID {category_id} retrieved successfully",
        data=artworks_list,
        status_code=200
    )