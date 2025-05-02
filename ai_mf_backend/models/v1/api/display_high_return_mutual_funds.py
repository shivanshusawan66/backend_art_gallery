from pydantic import BaseModel
from typing import List, Dict, Any


class HighReturnMutualFundsResponse(BaseModel):
    status: bool
    message: str
    page: int
    total_pages: int
    total_data: int
    data: List[Dict[str, Any]]
    status_code: int
