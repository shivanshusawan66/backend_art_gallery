from typing import Any, Dict, List, Optional
from ai_mf_backend.models.v1.api import Response

class MFCategoryOptionResponse(Response):
    pass

class MFSubCategoryOptionResponse(Response):
   pass

class MFDataCategorySubcategoryWise(Response):
    page: int
    total_pages: int
    total_data: int
    data: Optional[List[Dict[str, Any]]] = None



