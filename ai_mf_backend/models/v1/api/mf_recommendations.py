from ai_mf_backend.models.v1.api import Response
from typing import List, Dict, Any ,Optional

class MFRecommendationsResponse(Response):
    page: Optional[int] = None
    total_pages: Optional[int] = None
    total_data: Optional[int] = None
    data: List[Dict[str, Any]]