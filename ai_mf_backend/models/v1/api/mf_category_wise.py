from typing import Any, Dict, List, Optional
from ai_mf_backend.models.v1.api import Response

class MFCategoryOptionResponse(Response):
    pass

class MFDataCategorySubcategoryWise(Response):
    data: Optional[List[Dict[str, Any]]] = None

class MFSubCategoryOptionResponse(Response):
   pass