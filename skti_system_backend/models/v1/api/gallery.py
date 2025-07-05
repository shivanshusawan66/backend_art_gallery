from datetime import datetime
from pydantic import BaseModel
from typing import List, Any

from skti_system_backend.models.v1.api import Response


class ArtworkData(BaseModel):
    id: int
    title: str
    description: str
    category: str
    image_url: str
    tags: list[str]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

class ArtworksResponse(Response):
    data: list[ArtworkData] 

class CategoriesResponse(Response):
    data: list[Any]