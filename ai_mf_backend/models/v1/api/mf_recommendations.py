from ai_mf_backend.models.v1.api import Response
from typing import List, Dict, Any

class MFRecommendationsResponse(Response):
    page: int
    total_pages: int
    total_data: int
    data: List[Dict[str, Any]]