from typing import Any, Dict, List, Optional
from ai_mf_backend.models.v1.api import Response
    
class BlogCardResponse(Response):
    data: Optional[List[Dict[str, Any]]] = None
